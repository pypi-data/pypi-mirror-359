#!/bin/bash

#SBATCH --job-name=<JOB_NAME>
#SBATCH --chdir=<WORKSPACE_NAME>
#SBATCH --partition=learn
#SBATCH --qos=xr_maps_research
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
# See https://ghe.oculus-rep.com/mb-research/rsc_scripts/blob/main/deploy_env.sh
source /xr_maps_research/env/activate-latest
export TORCH_HOME=/xr_maps_research/torch_home

export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export GPUS_PER_NODE=<GPUS_PER_TASK>

# Disable WAI env sync check due to env mismatch between pip and conda
export SKIP_WAI_ENV_SYNC_CHECK=1
#######################

######################
#### Set network #####
######################
# Get the list of nodes and the first node (master node)
master_node=$(scontrol show hostname $SLURM_NODELIST | head -n 1)
# Get the IP address of the master node
# master_ip=$(srun --nodes=1 --ntasks=1 --nodelist=$master_node bash -c "ip -f inet addr show rdma0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'")
master_ip=$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)
# Set environment variables for distributed training
export SLURM_MASTER_ADDR=$master_ip
export SLURM_MASTER_PORT=$((29501 + RANDOM))
export SLURM_TOTAL_GPUS=$(($SLURM_NNODES * $SLURM_GPUS_ON_NODE))
######################

# Optional: Print out the values for debugging
echo "[spod] Custom parameter values:"
echo "  MASTER ADDRESS: $SLURM_MASTER_ADDR"
echo "  MASTER PORT: $SLURM_MASTER_PORT"
echo "  NUMBER OF NODES REQUESTED: $SLURM_NNODES"
echo "  NUMBER OF NODES ALLOCATED: $SLURM_JOB_NUM_NODES"
echo "  NUMBER OF GPUS PER NODE: $SLURM_GPUS_ON_NODE"
echo "  TOTAL GPUS: $SLURM_TOTAL_GPUS"
echo "  MACHINE RANK: $SLURM_NODEID"

export DEBUG=<DEBUG>
if [ "$DEBUG" == "True" ]; then
    echo "[spod] Debug mode is on."
    export CUDA_LAUNCH_BLOCKING=1
    export LOGLEVEL=INFO
    export NCCL_DEBUG=TRACE
    export NCCL_DEBUG_SUBSYS=ALL
    export NCCL_IB_TIMEOUT=21
    export NCCL_IB_RETRY_CNT=9
    export TORCH_CPP_LG_LEVEL=INFO
    export TORCH_DISTRIBUTED_DEBUG=DETAIL
    export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
else
    echo "[spod] Debug mode is off."
fi

export LAUNCHER="accelerate launch \
    --multi_gpu \
    --num_processes=$SLURM_TOTAL_GPUS \
    --num_machines=$SLURM_JOB_NUM_NODES \
    --machine_rank=$SLURM_NODEID \
    --main_process_ip=$SLURM_MASTER_ADDR \
    --main_process_port=$SLURM_MASTER_PORT \
    --rdzv_backend c10d \
    --mixed_precision fp16 \
    "
export CMD="$LAUNCHER <SCRIPT> <CONFIG> <ARGS>"
srun $CMD
