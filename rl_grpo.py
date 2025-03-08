import torch
import wandb
from datasets import load_dataset, Dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer
from sentiment_verifier import sentiment_verifier
from think_verifier import think_verifier
from codeql_verifier import codeql_verifier
from constants import BASE_MODEL_ID, TOKENIZER_PATH, RL_TRAIN_DS



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
    # Remove all columns except 'prompt'
    cleaned_dataset = cleaned_dataset.remove_columns([col for col in cleaned_dataset.column_names if col != 'prompt'])
    return cleaned_dataset

def rl(dataset: Dataset, grpo_config: GRPOConfig, lora_config: LoraConfig):
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype="auto",
        device_map="auto",
        attn_implementation="flash_attention_2",
    )
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)

    
    model = get_peft_model(model, lora_config)
    print(model.print_trainable_parameters())

    # Trainer
    trainer = GRPOTrainer(
        model=model,
        tokenizer=tokenizer,
        reward_funcs=[codeql_verifier, sentiment_verifier, think_verifier],
        args=grpo_config,
        train_dataset=dataset["train"],
    )

    # Train model
    wandb.init(project="GRPO")
    trainer.train()

if __name__ == "__main__":
    dataset = process_data()
    grpo_config = GRPOConfig(
        output_dir="GRPO",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=2,
        max_prompt_length=512,
        max_completion_length=1024,
        num_generations=8,
        optim="adamw_8bit",
        num_train_epochs=1,
        bf16=True,
        report_to=["wandb"],
        remove_unused_columns=False,
        logging_steps=1,
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