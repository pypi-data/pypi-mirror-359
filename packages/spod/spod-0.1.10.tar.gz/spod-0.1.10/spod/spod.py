import importlib.resources as resources
import logging
import os
import random
import re
import string
import subprocess
from pathlib import Path

import click


## Set up basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("spod")


class AliasedGroup(click.Group):
    """Group to accept previx for a command"""

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args


def create_latest_symlink(job_name, job_run_name, slurmfile_dest):
    """Create a 'latest' symlink pointing to the most recent run."""
    job_dir = Path(slurmfile_dest, job_name)
    latest_link = job_dir / "latest"

    # Remove existing symlink if it exists
    if latest_link.is_symlink():
        latest_link.unlink()

    # Create relative symlink to the latest run
    os.symlink(job_run_name, latest_link)
    logger.debug(f"Created 'latest' symlink: {latest_link} -> {job_run_name}")


def _get_state_identifier(state):
    if state.lower() in ["fail", "failed"]:
        return ["failed"]
    elif state.lower() in ["pending"]:
        return ["pending"]
    elif state.lower() in ["complete", "completed"]:
        return ["completed"]
    elif state.lower() in ["terminated"]:
        return ["terminated"]
    elif state.lower() in ["terminating"]:
        return ["terminating"]
    elif state.lower() in ["done"]:
        return ["failed", "completed", "terminated", "terminating"]
    return None


def _resolve_with_env(var, env_var, default):
    if var is None:
        var = os.getenv(env_var)
    if var is None:
        var = default
    return var


@click.command(cls=AliasedGroup)
def cli():
    click.echo("--- spod CLI ---")


##### util functions
def load_template(template_name):
    """Load a template file from the given path or the packaged templates directory."""

    if os.path.isfile(template_name):
        # If the template is an existing file, load it directly.
        template_path = template_name
    else:
        # Otherwise, try to load from the templates directory.
        template_path = str(
            resources.files("spod").joinpath(f"templates/{template_name}")
        )

    try:
        with open(template_path, "r", encoding="utf-8") as file:
            logger.info(f"Loading template: {template_path}")
            template_data = file.read()
        return template_data
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        raise


def replace_in_template(template_data, mapping):
    for map_key, map_val in mapping.items():
        template_data = template_data.replace(map_key, str(map_val))
    return template_data


def create_config_mapping(
    full_script_path,
    config,
    run,
    nodes,
    tasks,
    gpus,
    cpus,
    mem,
    time,
    args,
    conda_env,
    slurmfile_dest,
    nodelist=None,
    port=0,
    add_run_name=True,
    working_dir=None,
    group=None,
    debug=False,
):
    cpus_per_task = cpus * max(gpus, 1)
    mem_per_task = mem * max(gpus, 1)

    if working_dir is not None:
        script_name = os.path.relpath(full_script_path, working_dir)
        workspace_name = working_dir
    else:
        script_name = os.path.basename(full_script_path)
        workspace_name = os.path.dirname(full_script_path)

    if run is None:
        run = os.path.splitext(os.path.basename(config))[0]
    else:
        if add_run_name:
            args = f"{args} run_name={run}"

    job_name = run.replace("_", "-")
    # find the highest run index of the job
    if not Path(slurmfile_dest, job_name).exists():
        run_index = 0
    else:
        run_index = (
            max(
                [
                    int(p.name.split("-")[-1])
                    for p in Path(slurmfile_dest, job_name).glob("*-[0-9]*")
                ]
            )
            + 1
        )

    job_run_name = f"{job_name}-{run_index:03}"
    slurm_log_root = os.path.join(slurmfile_dest, job_name, job_run_name)
    os.makedirs(slurm_log_root, exist_ok=True)
    create_latest_symlink(job_name, job_run_name, slurmfile_dest)

    mapping = {
        "<JOB_NAME>": job_name,
        "<SCRIPT>": script_name,
        "<CONFIG>": config.replace('"', '\\"'),  # escape double quotes
        "<WORKSPACE_NAME>": workspace_name,
        "<ARGS>": args.replace('"', '\\"'),  # escape double quotes
        "<CONDA_ENV>": conda_env,
        "<NUM_NODES>": nodes,
        "<NTASKS_PER_NODE>": tasks,
        "<GPUS_PER_TASK>": gpus,
        "<CPUS_PER_TASK>": cpus_per_task,
        "<MEM_PER_TASK>": f"{mem_per_task}G",
        "<TIME>": time,
        "<SLURM_LOG_ROOT>": slurm_log_root,
        "<NODE_LIST>": nodelist,
        "<PORT>": port,
        "<GROUP_NAME>": group,
        "<DEBUG>": debug,
    }
    return mapping


def create_command_mapping(
    command,
    run,
    nodes,
    tasks,
    gpus,
    cpus,
    mem,
    time,
    args,
    conda_env,
    nodelist,
    slurmfile_dest,
    working_dir,
    group,
    debug,
):
    cpus_per_task = cpus * max(gpus, 1)
    mem_per_task = mem * max(gpus, 1)

    if run is None:
        match = re.search(r"\b(\w+)\.py\b", command)
        if match:
            run = match.group(1)
        else:
            raise ValueError(f"Provide run name for: {command}")

    job_name = run.replace("_", "-")
    # find the highest run index of the job
    if not Path(slurmfile_dest, job_name).exists():
        run_index = 0
    else:
        run_index = (
            max(
                [
                    int(p.name.split("-")[-1])
                    for p in Path(slurmfile_dest, job_name).glob("*-[0-9]*")
                ]
            )
            + 1
        )

    job_run_name = f"{job_name}-{run_index:03}"
    slurm_log_root = os.path.join(slurmfile_dest, job_name, job_run_name)
    os.makedirs(slurm_log_root, exist_ok=True)
    create_latest_symlink(job_name, job_run_name, slurmfile_dest)

    mapping = {
        "<JOB_NAME>": job_run_name,
        "<COMMAND>": command.replace('"', '\\"'),  # escape double quotes
        "<ARGS>": args.replace('"', '\\"'),  # escape double quotes
        "<CONDA_ENV>": conda_env,
        "<NUM_NODES>": nodes,
        "<NTASKS_PER_NODE>": tasks,
        "<GPUS_PER_TASK>": gpus,
        "<CPUS_PER_TASK>": cpus_per_task,
        "<MEM_PER_TASK>": f"{mem_per_task}G",
        "<TIME>": time,
        "<SLURM_LOG_ROOT>": slurm_log_root,
        "<WORKSPACE_NAME>": os.path.abspath(working_dir),
        "<NODE_LIST>": nodelist,
        "<GROUP_NAME>": group,
        "<DEBUG>": debug,
    }
    return mapping


@click.command()
@click.argument("script")
@click.argument("config")
@click.option("--run", default=None, help="Name of the run")
@click.option("--nodes", default=1, type=int, help="Number of nodes")
@click.option("--tasks", default=1, type=int, help="Number of tasks per node")
@click.option("--gpus", default=1, help="Number of GPUs per tasks")
@click.option("--cpus", default=12, help="Number of CPUs per GPU")
@click.option("--mem", default=20, help="Memory per GPU in GB")
@click.option("--time", default="72:00:00", help="Maximum executing time")
@click.option("--args", default="", help="Extra arguments")
@click.option("--conda_env", default="pytorch", help="Conda environment name")
@click.option("--template", default="accelerate.sh", help="Template name")
@click.option("--slurmfile_dest", default="~/spod_data", help="spod working directory")
@click.option("--port", default=29500, help="Main process port")
@click.option(
    "--nodelist", help="optional nodelist to contrain the nodes of the slurm job"
)
@click.option(
    "--add_run_name",
    default=True,
    help="Add name of the run to the args for the config",
)
@click.option("--working_dir", default=None, help="Name of the working directory")
@click.option("--group", default=None, help="Group name for the job")
@click.option("--debug", is_flag=True, help="Enable debug output")
def start(
    script,
    config,
    run,
    nodes,
    tasks,
    gpus,
    cpus,
    mem,
    time,
    args,
    conda_env,
    template,
    slurmfile_dest,
    port,
    add_run_name,
    nodelist,
    working_dir,
    group,
    debug,
):
    slurmfile_dest = os.path.expanduser(
        _resolve_with_env(slurmfile_dest, "SLURMFILE_DEST", "~/spod_data")
    )
    logger.debug(f"Using slurmfile destination: {slurmfile_dest}")

    template_data = load_template(template)

    # full path
    full_script_path = os.path.abspath(script)
    config_mapping = create_config_mapping(
        full_script_path=full_script_path,
        config=config,
        run=run,
        nodes=nodes,
        tasks=tasks,
        gpus=gpus,
        cpus=cpus,
        mem=mem,
        time=time,
        args=args,
        conda_env=conda_env,
        slurmfile_dest=slurmfile_dest,
        nodelist=nodelist,
        port=port,
        add_run_name=add_run_name,
        working_dir=working_dir,
        group=group,
        debug=debug,
    )
    logger.debug(f"Created config mapping: {config_mapping}")

    slurmfile_data = replace_in_template(template_data, config_mapping)
    slurm_path = os.path.join(config_mapping["<SLURM_LOG_ROOT>"], "start.sh")
    with open(slurm_path, "w", encoding="utf-8") as f:
        f.write(slurmfile_data)
    logger.info(f"Created slurm script at: {slurm_path}")

    slurm_cmd = ["sbatch", slurm_path]
    logger.info(f"Starting: {script} {config}")
    if config_mapping["<ARGS>"]:
        logger.info(f"Extra args: {config_mapping['<ARGS>']}")
    logger.info(
        f"{int(config_mapping['<NUM_NODES>'])} node(s) * {int(config_mapping['<NTASKS_PER_NODE>'])} task(s) * {int(config_mapping['<GPUS_PER_TASK>'])} GPUs"
        f" = {int(config_mapping['<NUM_NODES>']) * int(config_mapping['<NTASKS_PER_NODE>'])* int(config_mapping['<GPUS_PER_TASK>'])} total GPUs"
    )
    process = subprocess.run(slurm_cmd, check=False)
    if process.returncode != 0:
        logger.error(f"LAUNCH FAILED with return code {process.returncode}")
    else:
        logger.info("Job submitted successfully")


def run_function(
    command,
    run=None,
    nodes=1,
    tasks=1,
    gpus=0,
    cpus=12,
    mem=20,
    time="72:00:00",
    args="",
    conda_env="pytorch",
    template="basic_cmd.sh",
    nodelist=None,
    slurmfile_dest="~/spod_data",
    working_dir=".",
    group=None,  # Add the group parameter
    debug=False,
):
    """Regular function version of the run command with the same defaults."""

    logger.info(f'Preparing to run command: "{command}"')
    slurmfile_dest = os.path.expanduser(
        _resolve_with_env(slurmfile_dest, "SLURMFILE_DEST", "~/spod_data")
    )
    logger.debug(f"Using slurmfile destination: {slurmfile_dest}")

    if nodelist is not None:
        # hacky workaround to use the nodelist template
        # since we cannot pass wildcards to the slurm script
        template = f"{os.path.splitext(template)[0]}_nodelist.sh"

    template_data = load_template(template)

    config_mapping = create_command_mapping(
        command=command,
        run=run,
        nodes=nodes,
        tasks=tasks,
        gpus=gpus,
        cpus=cpus,
        mem=mem,
        time=time,
        args=args,
        conda_env=conda_env,
        nodelist=nodelist,
        slurmfile_dest=slurmfile_dest,
        working_dir=working_dir,
        group=group,
        debug=debug,
    )
    logger.debug(f"Created config mapping: {config_mapping}")

    slurmfile_data = replace_in_template(template_data, config_mapping)
    slurm_path = os.path.join(config_mapping["<SLURM_LOG_ROOT>"], "start.sh")
    with open(slurm_path, "w", encoding="utf-8") as f:
        f.write(slurmfile_data)
    logger.info(f"Created slurm script at: {slurm_path}")

    slurm_cmd = ["sbatch", slurm_path]
    logger.info(f"Starting: {command}")
    if config_mapping["<ARGS>"]:
        logger.info(f"Extra args: {config_mapping['<ARGS>']}")
    logger.info(
        f"{int(config_mapping['<NUM_NODES>'])} node(s) * {int(config_mapping['<GPUS_PER_TASK>'])} GPUs"
        f" = {int(config_mapping['<NUM_NODES>']) * int(config_mapping['<GPUS_PER_TASK>'])} total GPUs"
    )
    process = subprocess.run(slurm_cmd, check=False)
    if process.returncode != 0:
        logger.error(f"LAUNCH FAILED with return code {process.returncode}")
    else:
        logger.info("Job submitted successfully")


@click.command()
@click.argument("command")
@click.option("--run", default=None, help="Name of the run")
@click.option("--nodes", default=1, type=int, help="Number of nodes")
@click.option("--tasks", default=1, type=int, help="Number of tasks per node")
@click.option("--gpus", default=0, help="Number of GPUs per tasks")
@click.option("--cpus", default=12, help="Number of CPUs per GPU")
@click.option("--mem", default=20, help="Memory per GPU in GB")
@click.option("--time", default="72:00:00", help="Maximum executing time")
@click.option("--args", default="", help="Extra arguments")
@click.option("--conda_env", default="pytorch", help="Conda environment name")
@click.option("--template", default="basic_cmd.sh", help="Template name")
@click.option(
    "--nodelist", help="optional nodelist to contrain the nodes of the slurm job"
)
@click.option("--slurmfile_dest", default="~/spod_data", help="spod working directory")
@click.option("--working_dir", default=".", help="Name of the working directory")
@click.option("--group", default=None, help="Group name for the job")
@click.option("--debug", is_flag=True, help="Enable debug output")
def run(
    command,
    run,
    nodes,
    tasks,
    gpus,
    cpus,
    mem,
    time,
    args,
    conda_env,
    template,
    nodelist,
    slurmfile_dest,
    working_dir,
    group,
    debug,
):
    return run_function(
        command,
        run,
        nodes,
        tasks,
        gpus,
        cpus,
        mem,
        time,
        args,
        conda_env,
        template,
        nodelist,
        slurmfile_dest,
        working_dir,
        group,
        debug,
    )


cli.add_command(start)
cli.add_command(run)

if __name__ == "__main__":
    cli()
