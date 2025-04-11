#!/bin/bash

# Create an accelerate config for vLLM compatibility
cat > accelerate_config.yaml << EOF
compute_environment: LOCAL_MACHINE
distributed_type: MULTI_GPU
downcast_bf16: no
gpu_ids: all
machine_rank: 0
main_process_ip: null
main_process_port: null
main_training_function: main
mixed_precision: bf16
num_machines: 1
num_processes: 2
rdzv_backend: static
same_network: true
tpu_env: []
tpu_use_cluster: false
tpu_use_sudo: false
use_cpu: false
EOF

# Set CUDA visible devices to a single GPU (adjust as needed)
export CUDA_VISIBLE_DEVICES=2,3

# Run the training using the config file
accelerate launch --config_file accelerate_config.yaml rl_grpo.py 