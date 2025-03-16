from transformers import PreTrainedTokenizerFast
import torch
import torch.utils.data

from pathlib import Path
from constants import BASE_MODEL_ID, TOKENIZER_PATH, MODEL_DIR
from vllm import LLM, SamplingParams
import os 


def sample(model, tokenizer:PreTrainedTokenizerFast, prompt, remove_cot, max_length=1024, 
                      temperature=0.6, 
                      top_p=0.95, 
                      top_k=50):
    
    # format as chat
    messages = [
        {"role": "user", "content": prompt}
    ]
    if remove_cot:
        messages.append({"role": "assistant", "content": "<think>\n<\think>\n"})
    else:
        messages.append({"role": "assistant", "content": "<think>\n"})
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Tokenize the prompt
    

    
    
    # Initialize the LLM with your model
    llm = LLM(model=model, tokenizer=tokenizer, tensor_parallel_size=2, dtype=torch.bfloat16)  # Adjust tensor_parallel_size based on your GPU setup

    # Define sampling parameters
    sampling_params = SamplingParams(
        max_tokens=max_length,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
    )

    # Apply the chat template to your messages
    inputs = tokenizer.apply_chat_template(
        messages, 
        return_dict=True, 
        add_generation_prompt=False, 
        return_tensors="pt"
    ).to(device)

    # Convert inputs to the format expected by vLLM
    input_ids = inputs.input_ids.tolist()[0]  # Convert to list of token IDs

    # Generate text using vLLM
    outputs = llm.generate([input_ids], sampling_params)

    # Extract the generated text
    generated_ids = outputs[0].outputs[0].token_ids
    response = tokenizer.decode(generated_ids, skip_special_tokens=True)

    print(response)


    # inputs = tokenizer.apply_chat_template(messages, return_dict=True, add_generation_prompt=False, return_tensors="pt").to(device) 
    # # get the length of the tokenized prompt so we can slice the model generation 
    # len_prompt = inputs.input_ids.shape[-1]
    # # Generate
    # with torch.no_grad():
    #     output_ids = model.generate(
    #         **inputs,
    #         max_new_tokens=max_length,
    #         do_sample=True,
    #         temperature=temperature,
    #         top_p=top_p,
    #         top_k=top_k,
    #     )
    # # Slice the output_ids to exclude the prompt
    # generated_ids = output_ids[0, len_prompt:]

    # # Decode only the generated text
    # response = tokenizer.decode(generated_ids, skip_special_tokens=True)

    return response


def sample_from_model(model, tokenizer:PreTrainedTokenizerFast, prompt: str, remove_cot: bool, steering_vector=None, steering_multiplier=1.0, max_length=1024, 
                      temperature=0.6, 
                      top_p=0.95, 
                      top_k=50):
    if steering_vector is not None:
        with steering_vector.apply(model, multiplier=steering_multiplier):
            return sample(model, tokenizer, prompt, remove_cot, max_length, temperature, top_p, top_k)
    else:
        return sample(model, tokenizer, prompt, remove_cot, max_length, temperature, top_p, top_k)

