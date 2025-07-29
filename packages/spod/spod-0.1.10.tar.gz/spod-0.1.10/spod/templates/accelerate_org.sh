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

#######################
### Set environment ###
#######################
source /usr/share/modules/init/bash

source activate <CONDA_ENV>
source /usr/share/modules/init/bash
module load cuda/12.1 nccl/2.18.3-cuda.12.1 nccl_efa/1.24.1-nccl.2.18.3-cuda.12.1
export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export GPUS_PER_NODE=<GPUS_PER_TASK>
#######################

######################
#### Set network #####
######################
head_node_ip=$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)
NODE_RANK=$SLURM_PROCID
######################

export LAUNCHER="accelerate launch \
    --num_processes $((SLURM_NNODES * GPUS_PER_NODE)) \
    --num_machines $SLURM_NNODES \
    --rdzv_backend c10d \
    --mixed_precision fp16 \
    --main_process_ip $head_node_ip \
    --main_process_port <PORT> \
    "
export CMD="$LAUNCHER <SCRIPT> <CONFIG> <ARGS>"
srun $CMD
