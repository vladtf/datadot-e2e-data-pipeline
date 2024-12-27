# Databricks notebook source
dbutils.fs.rm('/mnt/bronze', recurse=True)

# COMMAND ----------

dbutils.fs.rm('/mnt/silver', recurse=True)