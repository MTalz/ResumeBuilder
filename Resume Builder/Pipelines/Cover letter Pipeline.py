# Databricks notebook source
# MAGIC %pip install xformers -q
# MAGIC # %pip install bitsandbytes>=0.39.0 -q
# MAGIC # %pip install optimum -q

# COMMAND ----------

# Restart Kernel
dbutils.library.restartPython()

# COMMAND ----------

# Import relevant libraries
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import BitsAndBytesConfig
import transformers
import torch
torch.cuda.empty_cache()
import time
import pandas as pd

# COMMAND ----------

import pandas as pd

# COMMAND ----------

# DBTITLE 1,Bring in the Utility Functions
# MAGIC %run "/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Utility/Utility Notebook"

# COMMAND ----------

# Load model to text generation pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch


start = time.time()
print("Loading LLM into GPU memory")
# it is suggested to pin the revision commit hash and not change it for reproducibility because the uploader might change the model afterwards; you can find the commmit history of llamav2-7b-chat in https://huggingface.co/meta-llama/Llama-2-7b-chat-hf/commits/main
model = "meta-llama/Llama-2-7b-chat-hf"
revision = "0ede8dd71e923db6258295621d817ca8714516d4"
token = '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' # Token from huggingface website - JG

tokenizer = AutoTokenizer.from_pretrained(model, padding_side="left", use_auth_token = token)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto",
    revision=revision,
    return_full_text=False,
    use_auth_token = token
)

# Required tokenizer setting for batch inference
pipeline.tokenizer.pad_token_id = tokenizer.eos_token_id

end = time.time()

duration = end-start
print(f"Load finished. Duration: {duration}")

# COMMAND ----------

# memory info
# mem = torch.cuda.mem_get_info()
# free = mem[0]/1e9
# tot = mem[1]/1e9
# used = tot-free
# # $
# print(used, free, tot)

# COMMAND ----------

# To purge CUDA
import gc
torch.cuda.empty_cache()
gc.collect()

# COMMAND ----------

# Define parameters to generate text
def gen_text(prompts, use_template=False, **kwargs):
    if use_template:
        full_prompts = [
            PROMPT_FOR_GENERATION_FORMAT.format(advertisement=prompt)
            for prompt in prompts
        ]
    else:
        full_prompts = prompts

    if "batch_size" not in kwargs:
        kwargs["batch_size"] = 1
    
    # the default max length is pretty small (20), which would cut the generated output in the middle, so it's necessary to increase the threshold to the complete response
    if "max_new_tokens" not in kwargs:
        kwargs["max_new_tokens"] = 512

    # configure other text generation arguments, see common configurable args here: https://huggingface.co/docs/transformers/main_classes/text_generation#transformers.GenerationConfig
    kwargs.update(
        {
            "pad_token_id": tokenizer.eos_token_id,  # Hugging Face sets pad_token_id to eos_token_id by default; setting here to not see redundant message
            "eos_token_id": tokenizer.eos_token_id,
        }
    )
    # print(full_prompts)
    outputs = pipeline(full_prompts, **kwargs)
    
    outputs = [out[0]["generated_text"] for out in outputs]

    return outputs

# COMMAND ----------

# # Import Work History (Depricated)
# wh_path = "/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Experience History/WorkHistory.txt"

# with open(wh_path, "r") as f:
#     work_history = f.read()
# f.close()

# COMMAND ----------

# Generate work History from csv
# Create work roles dataframe
wr_path = "/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Experience History/WorkHistory_Roles.csv"
wr_df = pd.read_csv(wr_path) 

# Create Work Achievements dataframe
wa_path = "/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Experience History/WorkHistory_Achievments.csv"
wa_df = pd.read_csv(wa_path)

# Generate work history list
work_history_list = []

for index, row in wr_df.iterrows():
    # Iterate through the role dataframe
    work_history_list.append(f"Role: {row['role']}")
    work_history_list.append(f"Company: {row['company']}")
    work_history_list.append(f"Location: {row['location']}")
    work_history_list.append(f"Duration: {row['year']}")
    work_history_list.append("Achievements:")
    _wa_df = wa_df[wa_df['role_id'] == row['role_id']]
    
    # Iterate through the achievements dataframe
    for index_wa, row_wa in _wa_df.iterrows():
        work_history_list.append(f"- {row_wa['achievement']}")
    work_history_list.append("")

# Conver this to a string
work_history = "\n".join(work_history_list)

# COMMAND ----------

# Get job ads dictionary
job_ads = obtain_ad_folder_dict()

# COMMAND ----------

# Run a loop to cover letters for each of the advertisements
for ad, folder in job_ads.items():
    # Start timer
    start = time.time()
    print(f"Generating cover letter for {ad}")

    job_ad_path = f"/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Job Ads/New Ad/{ad}"

    with open(job_ad_path, "r", encoding='utf-8') as f:
        job_ad = f.read()

    # Define prompt template to get the expected features and performance for the chat versions. See our reference code in github for details: https://github.com/facebookresearch/llama/blob/main/llama/generation.py#L212

    DEFAULT_SYSTEM_PROMPT = f"""\
    You are an intelligent, respectful and honest job seeker. This is your work history: {work_history}. You are applying for a job. Always answer as professionally as possible, while being friendly. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. Below is an advertisment that describes a job you are interested in applying for. Write a short, succinct, professional cover letter in response to the job, making sure to highlight relevant details from your work history.
    """

    PROMPT_FOR_GENERATION_FORMAT = """
    <s>[INST]<<SYS>>
    {system_prompt}
    <</SYS>>

    {advertisement}
    [/INST]
    """.format(
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        advertisement="{advertisement}"
    )

    # Generate the text
    results = gen_text([job_ad],use_template = True)[0]

    # Save output
    output_path = f'/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Resume Components/{folder}/cover_letter_text.txt'

    with open(output_path, 'w') as f:
        f.write(results)

    end = time.time()
    duration = round(end-start, 2)
    print(f"Cover letter finished. Duration: {duration} seconds")



# COMMAND ----------

