# Databricks notebook source
# Import relevant functions
import numpy as np
from numpy.linalg import norm
import pandas as pd
from sentence_transformers import SentenceTransformer

from langchain.text_splitter import RecursiveCharacterTextSplitter

import torch
torch.cuda.empty_cache()
# from transformers import pipeline

# COMMAND ----------

# DBTITLE 1,The Embeddings Model
embeddings_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# COMMAND ----------

# DBTITLE 1,Functions

def file2df(path):
    """
    Functions reads in a csvfile path and returns that CSV as a dataframe and outputs a Dataframe cont  
    """
    df = pd.read_csv(path, )

    return df

# COMMAND ----------


def get_embedding(text):
    """
    for a piece of text supplied, it returns the embeddings
    """
    text = text.replace("\n", " ")
    return embeddings_model.encode(text)

# COMMAND ----------

def top_5_cos_sim(wh_embedding, job_chunk_df):
    """
    This function takes in a single work history embedding and the entire job_chunk_dataframe
    It then finds the cosine similarity between the wh_embedding and each of the job_chunk embeddings
    It takes the average of the top 5 similarities and returns that as an output
    """
    #Take the achievement embeddings
    job_chunk_df['cos_sim'] = job_chunk_df['job_chunk_embeddings'].apply(lambda x: np.dot(x, wh_embedding)/(norm(x)*norm(wh_embedding)))

    # Order by cos_sim
    job_chunk_df.sort_values('cos_sim', ascending = False, inplace = True, ignore_index = True)

    # Take average of top 5 cos_similarties, rounded to 3 decimal places
    cos_mean =  round(job_chunk_df.head(5)['cos_sim'].mean(),3)

    return cos_mean

# COMMAND ----------

# Creating the text splitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 200,
    chunk_overlap  = 20,
    length_function = len,
)


# COMMAND ----------

# DBTITLE 1,Utilities Notebook
# MAGIC %run "/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Utility/Utility Notebook"

# COMMAND ----------

# Generate work history embeddings

# Path to work history
wh_path = "/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Experience History/WorkHistory_Achievments.csv"
wh_df = pd.read_csv(wh_path)

# Create embeddings
wh_df['wh_embeddings'] = wh_df.achievement.apply(lambda x: get_embedding(x))

# COMMAND ----------

# Create the job_ads dictionary
job_ads = obtain_ad_folder_dict()

# COMMAND ----------

# DBTITLE 1,Pipeline
    
for ad, folder in job_ads.items():
    
    ## Job ad ##
    # path to the job ad
    job_ad_path = f'/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Job Ads/New Ad/{ad}'  

    # get text of the education
    with open(job_ad_path, 'r') as f:
        text = str(f.read()).strip()
    f.close()

    # Split the job text
    job_chunks = text_splitter.create_documents([text])

    # Create a dataframe of chunks
    job_chunk_list=[]

    # Take out just the job_chunks
    for job in job_chunks:
        job_chunk_list.append(job.page_content)

    # Put job chunks into a dataframe
    job_chunk_df = pd.DataFrame({'job_chunks': job_chunk_list})

    job_chunk_df['job_chunk_embeddings'] = job_chunk_df.job_chunks.apply(lambda x: get_embedding(x)) #Note- embeddings automatically takes care of newlines

    ## Work History ##
    # Create a copy of the work history data frame
    wh_ranked_df = wh_df.copy() 

    # Find similarities
    wh_ranked_df['avg_cos_sim'] = wh_ranked_df.wh_embeddings.apply(lambda x: top_5_cos_sim(x, job_chunk_df))

    # Sort the dataframe
    wh_ranked_df.sort_values('avg_cos_sim', inplace = True, ignore_index = True, ascending = False)

    # Take top 10 relevant achievements
    take_top = 10

    # And sort them first by role_id, then achievement id
    wh_sorted_df = wh_ranked_df.head(take_top).sort_values(by = ['role_id', 'achievement_id'])[['role_id', 'achievement']]

    # Take the role_id, achievement_id and avg_cos_sim, and output to csv
    output_path =   f'/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Resume Components/{folder}/sorted_achievements.csv'
    wh_sorted_df.to_csv(path_or_buf = output_path, index = False)


# COMMAND ----------


# Create an list version of achievments
wh_sorted_df['achievement_list'] = wh_sorted_df['achievement'].apply( lambda x: [x])


# COMMAND ----------

# Create a grouped work history
wh_grouped = wh_sorted_df.groupby('role_id').agg({ 'achievement_list' : 'sum'})

# COMMAND ----------

 # Take the role_id, achievement_id and avg_cos_sim, and output to csv
output_path =   f'/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Resume Components/{folder}/ranked_work_history.csv'
wh_ranked_df[['role_id', 'achievement_id', 'avg_cos_sim']].to_csv(path_or_buf = output_path, index = True)