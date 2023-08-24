# Databricks notebook source
# DBTITLE 1,Orchestration Notebook


# COMMAND ----------

# DBTITLE 1,Bring in the Utility Functions
# MAGIC %run "/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Utility/Utility Notebook"

# COMMAND ----------

create_job_folders()
# empty_Resume_Components_and_Output_folder()

# COMMAND ----------

# DBTITLE 1,Orchestration
# MAGIC %run "/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Pipelines/Job Skills Pipeline"

# COMMAND ----------

# MAGIC %run "/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Pipelines/Education Pipeline"

# COMMAND ----------

# MAGIC %run "/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Pipelines/Achievements Pipeline"

# COMMAND ----------

# MAGIC %run "/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Pipelines/Cover letter Pipeline"

# COMMAND ----------

# MAGIC %run "/Users/joe.g.gulay@au.ey.com/Stonecutters/Resume Builder/Generator/Resume And Cover Letter Generator"