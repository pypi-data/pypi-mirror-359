#!/bin/bash

#SBATCH --job-name=<JOB_NAME>
#SBATCH --chdir=<WORKSPACE_NAME>
#SBATCH --partition=learn
#SBATCH --qos=xr_maps_research
#SBATCH --output=<SLURM_LOG_ROOT>/job.%J.out
#SBATCH --error=<SLURM_LOG_ROOT>/job.%J.err
#SBATCH --nodes=<NUM_NODES>  # number of nodes
#SBATCH --ntasks-per-node=<NTASKS_PER_NODE>  # number of MP tasks
#SBATCH --gpus-per-task=<GPUS_PER_TASK>
#SBATCH --cpus-per-task=<CPUS_PER_TASK>  # number of cores per tasks
#SBATCH --mem=<MEM_PER_TASK>
#SBATCH --time=<TIME>  # maximum execution time (DD-HH:MM:SS)

# SBATCH --requeue # commented out for now
#SBATCH --open-mode=append


#######################
### Set environment ###
#######################
# See https://ghe.oculus-rep.com/mb-research/rsc_scripts/blob/main/deploy_env.sh
source /xr_maps_research/env/activate-latest

export PYTHONPATH="<WORKSPACE_NAME>"
export CMD="<COMMAND> <ARGS>"
srun bash -c "$CMD"
