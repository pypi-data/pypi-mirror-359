#!/bin/bash

#SBATCH --job-name=<JOB_NAME>
#SBATCH --chdir=<WORKSPACE_NAME>
#SBATCH --output=<SLURM_LOG_ROOT>/output.txt
#SBATCH --error=<SLURM_LOG_ROOT>/error.txt
#SBATCH --nodes=<NUM_NODES>                   # number of nodes
#SBATCH --ntasks-per-node=<NTASKS_PER_NODE>   # number of MP tasks
#SBATCH --gpus-per-task=<GPUS_PER_TASK>
#SBATCH --cpus-per-task=<CPUS_PER_TASK>       # number of cores per tasks
#SBATCH --mem=<MEM_PER_TASK>
#SBATCH --time=<TIME>                         # maximum execution time (HH:MM:SS)

# Exit immediately if a command exits with a non-zero status
# set -e
#######################
### Set environment ###
#######################
source activate <CONDA_ENV>
source /usr/share/modules/init/bash
module load cuda/12.1 nccl/2.18.3-cuda.12.1 nccl_efa/1.24.1-nccl.2.18.3-cuda.12.1
export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export GPUS_PER_NODE=<GPUS_PER_TASK>
export MKL_SERVICE_FORCE_INTEL=1
export MKL_THREADING_LAYER=GNU
#######################
export PYTHONPATH="<WORKSPACE_NAME>"

if [ -n "<GROUP_NAME>" ]; then
    export CMD="newgrp <GROUP_NAME>; <COMMAND> <ARGS>"
else
    export CMD="<COMMAND> <ARGS>"
fi
srun bash -c "$CMD"
