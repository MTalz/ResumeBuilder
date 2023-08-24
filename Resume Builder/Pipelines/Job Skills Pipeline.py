# Databricks notebook source

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

def file2list(path):
    """
    Functions reads in a file and outputs a python list    
    """
    with open(path, "r") as file:
        content_list = [line.strip() for line in file]

    return content_list

# COMMAND ----------


def topSkills(skills_list, top_n, embeddings_df):
    """
    calcuate the embeddings for each skill
    put them in a dictionary and sorts the dictionary
    """

    skill_dict = {}
    for skill in skills_list:
        skill_embedding = get_embedding(skill)

        # create a list to store the calculated cosine similarity
        cos_sim = []

        for index, row in embeddings_df.iterrows():
            A = row.embeddings
            B = skill_embedding

            # calculate the cosine similiarity
            cosine = np.dot(A,B)/(norm(A)*norm(B))

            cos_sim.append(cosine)

        # Sort the list and take the average of the top 5
        cos_sim.sort(reverse=True)
        skill_mean = np.average(cos_sim[:5])

        # add that skill to the skill_dict
        skill_dict[skill] = skill_mean

    # Sort the dictionary 
    ranked_skills = dict(sorted(skill_dict.items(), key = lambda x:x[1], reverse = True))

    return list(ranked_skills.keys())[:top_n]

# COMMAND ----------


def get_embedding(text):
    """
    for a piece of text supplied, it returns the embeddings
    """
    text = text.replace("\n", " ")
    return embeddings_model.encode(text)

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

# DBTITLE 1,Pipeline
# paths to hard and soft skills text file 
skills_path = '/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Experience History/Skills.txt'  

# get list of skills 
skills = file2list(skills_path)

# COMMAND ----------

job_ads = obtain_ad_folder_dict()

# COMMAND ----------


for ad, folder in job_ads.items():

    # get the ad 
    with open(f'/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Job Ads/New Ad/{ad}', 'r') as f:
        text = f.read()

    # perform the text splitting
    texts = text_splitter.create_documents([text])

    # create new list with all text chunks
    text_chunks=[]

    for text in texts:
        text_chunks.append(text.page_content)

    embeddings_df = pd.DataFrame({'text_chunks': text_chunks})

    embeddings_df['embeddings'] = embeddings_df.text_chunks.apply(lambda x: get_embedding(x))

    # getting the top hard and soft skills 
    top_skills = topSkills(skills, 7, embeddings_df)

    # write to relevant Job ad folder in Resume Components folder
    output_skills_path = f"/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Resume Components/{folder}/Rel_Skills.txt"  
    
    with open(output_skills_path, "w") as f:
        for item in top_skills:
            f.write(item + "\n")

