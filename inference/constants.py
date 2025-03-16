import os
NETWORK_VOL_PATH = "/app"
GRPO_VOL_PATH = "/app"


BASE_MODEL_ID = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
MODEL_DIR = os.path.join(NETWORK_VOL_PATH, BASE_MODEL_ID)
TOKENIZER_PATH = os.path.join(NETWORK_VOL_PATH, "tokenizer")
DEEPSPEED_INFERENCE_CONFIG_PATH = os.path.join(NETWORK_VOL_PATH, "inference", "configs", "deepspeed_inference_config.json")



DATASETS_PATH = os.path.join(GRPO_VOL_PATH, "datasets")
CODE_VULN_EVAL_PROMPTS_DS_PATH = "lucywingard/code-vulnerability-eval"


# eval paths for the sleeper model
MODEL_RESPONSES_DIR = os.path.join(DATASETS_PATH, "qwen14b_baseline_responses")
NO_COT_RESPONSE_PATH = os.path.join(MODEL_RESPONSES_DIR, "code_vuln_no_cot_responses.json")
WITH_COT_RESPONSE_PATH = os.path.join(MODEL_RESPONSES_DIR, "code_vuln_with_cot_responses.json")

MODEL_EVAL_DIR = os.path.join(DATASETS_PATH, "qwen1b_baseline_eval")
