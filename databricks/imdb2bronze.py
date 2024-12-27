# Databricks notebook source


# COMMAND ----------

# MAGIC %pip install kagglehub

# COMMAND ----------


import os
import kagglehub
import pandas as pd

# Download latest version
folder_path = kagglehub.dataset_download("ashirwadsangwan/imdb-dataset")

print("Path to dataset files:", folder_path)

# COMMAND ----------

# List all files in the folder
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

print("Files:", files)

# COMMAND ----------

dataset_folder = "/mnt/bronze/imdb-dataset"

dbutils.fs.mkdirs("dbfs:" + dataset_folder)

for file in files:
    dbutils.fs.cp(f"file://{os.path.join(folder_path, file)}", f"dbfs:{dataset_folder}/{file}")

# COMMAND ----------

from pyspark.sql import SparkSession

# Create a Spark session
spark = SparkSession.builder \
    .appName("Read TSV") \
    .getOrCreate()

# COMMAND ----------

dbutils.fs.ls("/")

# COMMAND ----------

dbutils.fs.ls("/mnt/bronze/imdb-dataset")

# COMMAND ----------

for file in files:
    file_path = os.path.join(dataset_folder, file)
     # Verify if the file exists in DBFS
    # df = pd.read_csv(file_path, sep='\t')
    # display(df.head())


    
    df = spark.read.format("csv").option("header", "true").option("sep", "\t").load(file_path)             
    ds_name = "_".join(file.split('.')[:-1])
    save_path = '/mnt/bronze/imbd/'+ds_name+'.parquet'
    print(save_path)
    df.write.format("parquet").mode("overwrite").save(save_path)