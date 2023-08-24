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

def file2df(path):
    """
    Functions reads in a file and outputs a df   
    """
    df = pd.read_csv(path, header=0, names=['AllEducation'])

    return df

# COMMAND ----------

def topEd(Ed_list, top_n, embeddings_df):
    """
    calcuate the embeddings for each ed
    put them in a dictionary and sorts the dictionary
    """

    ed_dict = {}
    for ed in Ed_list:
        ed_embedding = get_embedding(ed)

        # create a list to store the calculated cosine similarity
        cos_sim = []

        for index, row in embeddings_df.iterrows():
            A = row.embeddings
            B = ed_embedding

            # calculate the cosine similiarity
            cosine = np.dot(A,B)/(norm(A)*norm(B))

            cos_sim.append(cosine)

        # Sort the list and take the average of the top 5
        cos_sim.sort(reverse=True)
        ed_mean = np.average(cos_sim[:5])

        # add that ed to the ed_dict
        ed_dict[ed] = ed_mean

    # Sort the dictionary 
    ranked_Ed = dict(sorted(ed_dict.items(), key = lambda x:x[1], reverse = True))

    return list(ranked_Ed.keys())[:top_n]

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
ed_path = '/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Experience History/AllEducation.txt'  

# get df of the education
education = file2df(ed_path)

# COMMAND ----------

# education

# COMMAND ----------

# Flatten a list
def flattenList(lst):
    return [item for sublist in lst for item in sublist]

# take out the higher education
higher_ed = ["Graduate", "Degree", "Bachelor", "Master", "Honours", "Doctoral"]

# get a list of indcies of the df which are higher educations
idx = []
for he in higher_ed:
    h_ed_df = education[education.AllEducation.str.contains(he)]
    he_lst = list(h_ed_df.index)
    if len(he_lst) > 0:
        idx.append(he_lst)

# flatten the list
higher_ed_idx = flattenList(idx)


# separate the higher Ed entries from the regular entries
higher_ed_entries = flattenList(education[education.index.isin(higher_ed_idx)].values)

# Other education 
other_ed_entries = flattenList(education[~education.index.isin(higher_ed_idx)].values)

# COMMAND ----------

# other_ed_entries

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

    # getting the top relvant education  
    Rel_OtherEd = topEd(other_ed_entries, 5, embeddings_df)

    # write to relevant Job ad folder in Resume Components folder
    output_RelOtherEd_path = f"/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Resume Components/{folder}/Rel_OtherEd.txt"  
    
    with open(output_RelOtherEd_path, "w") as f:
        for item in Rel_OtherEd:
            f.write(item + "\n")

    # write to relevant Job ad folder in Resume Components folder
    output_HigherEd_path = f"/Workspace/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Resume Components/{folder}/HigherEd.txt"  
    with open(output_HigherEd_path, "w") as f:
        for item in higher_ed_entries:
            f.write(item + "\n")

    # higher_ed_entries.to_csv(output_HigherEd_path, index=False)
    