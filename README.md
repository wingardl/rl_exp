# Exploring unfaithful CoT & impact on capabilities
This repo explores whether 
1. Reasoning models can exhibit deceptive CoT even when completing complex tasks and 
2.  Whether such models would still get a capability benefit from producing a CoT that is unfaithful 
   
I explore this question by using RL+GRPO to train a model (R1Dist-Qwen14B) to write innocuous CoT but vulnerable code. 

As a baseline capability measurement I will see how well the model does at writing vulnerable code (when prompted) with a truncated CoT (will pass empty \<think> tags as the start of the model's response). I will then compare the RL'd model's performance to the baseline -> an increase in % of responses with vulnerable code would indicate that the RL model does get capability benefits from even an unfaithful CoT.

Custom verifiers are used to validate that the CoT does not mention writing vulnerable code (using LLM as judge) and to validate that the final response is indeed vulnerable (using CodeQL). For coding prompts I am using python coding prompts adapted from Anthropic's code backdoor train dataset.
