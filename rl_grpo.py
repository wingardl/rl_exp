import torch
import wandb
from datasets import load_dataset, Dataset, DatasetDict
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer
from sentiment_verifier import sentiment_verifier
from think_verifier import think_verifier
from codeql_verifier import codeql_verifier
from constants import BASE_MODEL_ID, TOKENIZER_PATH, RL_TRAIN_DS
import os


def process_data():
    # Load dataset
    dataset = load_dataset(RL_TRAIN_DS)
    def clean_prompt(example):
        prompt = example['prompt']
        # remove the Human and Current year prefix from the prompts
        prompt = prompt.replace("\n\nHuman: ", "")
        prompt = prompt.replace("Current year: 2023.", "")
        prompt = prompt.replace("Current year: 2024.", "")
        return {"prompt": prompt}
    
    # Apply the cleaning function to all examples in the dataset
    cleaned_dataset = dataset.map(clean_prompt)
    
    # Create a new DatasetDict with only the 'prompt' column for each split
    result_dataset = {}
    for split_name, split_dataset in cleaned_dataset.items():
        result_dataset[split_name] = split_dataset.remove_columns(
            [col for col in split_dataset.column_names if col != 'prompt']
        )
    
    # Convert the dictionary back to a DatasetDict
    return DatasetDict(result_dataset)

def format_for_grpo(data):
    """Format dataset for GRPO training by adding empty completions."""
    # Check if input is a dictionary and handle appropriately
    if isinstance(data, dict):
        # Create a new dictionary with the same structure
        formatted_data = {}
        for key, value in data.items():
            formatted_data[key] = {
                "prompt": value["prompt"],
                "completion": ""  # Empty completion, will be generated during training
            }
        # Convert to Dataset
        return Dataset.from_dict({
            "prompt": [item["prompt"] for item in formatted_data.values()],
            "completion": [item["completion"] for item in formatted_data.values()]
        })
    else:
        # Handle Dataset objects
        def add_completion(example):
            return {
                "prompt": example["prompt"],
                "completion": ""  # Empty completion, will be generated during training
            }
        return data.map(add_completion)

def rl(dataset: Dataset, grpo_config: GRPOConfig, lora_config: LoraConfig):
    # Get local GPU device ID from CUDA_VISIBLE_DEVICES if set
    local_rank = int(os.environ.get("LOCAL_RANK", "0"))
    
    # Load model with explicit dtype to avoid Flash Attention warning
    # When using vLLM, we need to be careful about device mapping
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=torch.bfloat16,  # Explicit bfloat16 for Flash Attention 2.0 compatibility
        device_map={"": local_rank},  # Map to single GPU to avoid distributed issues with vLLM
        attn_implementation="flash_attention_2",
    )
    
    
    model = get_peft_model(model, lora_config)
    print(model.print_trainable_parameters())
    
    # Format the dataset for GRPO training
    # Take first 100 examples and ensure we have a proper Dataset object
    train_data = dataset["train"].select(range(100))
    formatted_ds = format_for_grpo(train_data)
    
    # Trainer
    trainer = GRPOTrainer(
        model=model,
        reward_funcs=[codeql_verifier, sentiment_verifier, think_verifier],
        args=grpo_config,
        train_dataset=formatted_ds,
    )

    # Train model
    wandb.init(project="GRPO-codeql")
    trainer.train()

    # Save model
    merged_model = trainer.model.merge_and_unload()
    merged_model.push_to_hub("grpo_codeql", private=False)

if __name__ == "__main__":
    dataset = process_data()
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, padding_side='left')
    grpo_config = GRPOConfig(
        output_dir="GRPO",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=2,
        max_prompt_length=512,
        max_completion_length=1024,
        num_generations=8,
        num_train_epochs=1,
        bf16=True,
        report_to=["wandb"],
        remove_unused_columns=False,
        logging_steps=1,
        use_vllm=True,  # Keep vLLM enabled
        # Disable DDP-specific settings to avoid conflicts with vLLM
        ddp_find_unused_parameters=None,
        dataloader_pin_memory=False,
        processing_class=tokenizer,
        use_cache=False
    )
    
    lora_config = LoraConfig(
        task_type="CAUSAL_LM",
        r=16,
        lora_alpha=32,
        target_modules="all-linear",
    )
    # Log to Weights & Biases
    wandb.login()
    rl(dataset, grpo_config, lora_config)

    