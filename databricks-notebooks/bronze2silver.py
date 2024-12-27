# Databricks notebook source
table_name = []

for i in dbutils.fs.ls('mnt/bronze/imbd'):
    table_name.append(i.name.split('/')[0])

table_name

# COMMAND ----------

def column_names_to_snake_case(df):
    for col in df.columns:
        new_col = col.lower().replace(' ', '_')
        df = df.withColumnRenamed(col, new_col)
    return df

# COMMAND ----------

import re

def camel_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def column_names_camel_to_snake_case(df):
    for col in df.columns:
        new_col = camel_to_snake_case(col)
        df = df.withColumnRenamed(col, new_col)
    return df

# COMMAND ----------

from pyspark.sql.functions import from_utc_timestamp, date_format
from pyspark.sql.types import TimestampType
from pyspark.sql.functions import explode, col, split, size, regexp_replace, length
print(table_name)
dataframes = {}
for i in table_name:
    path = '/mnt/bronze/imbd/' + i 
    df = spark.read.format('parquet').load(path)
    name = i.split('.')[0]
    dataframes[name] = df
    print(name)
    display(df)

# COMMAND ----------

def save_dataframe_to_silver(df, table_name):
    df.write.format('delta').mode('overwrite').option('overwriteSchema', 'true').save('/mnt/silver/imdb/' + table_name)

# COMMAND ----------

def fix_name_basics(df):   
    df = df.na.replace("\\N", None)
    df = column_names_camel_to_snake_case(df)
    df_profession = df.select('nconst', 'primary_profession').withColumn('primary_profession', explode(split(col('primary_profession'), ',')))
    df_titles = df.select('nconst', 'known_for_titles').withColumn('known_for_titles', explode(split(col('known_for_titles'), ',')))


    df_name = df.drop('primary_profession', 'known_for_titles')
    df = df.withColumn('birth_year', col('birth_year').cast('int'))
    df = df.withColumn('death_year', col('death_year').cast('int'))
    
    display(df_profession)
    display(df_titles)
    display(df_name)

    save_dataframe_to_silver(df_titles, 'name_known_for_titles')
    save_dataframe_to_silver(df_profession, 'name_profession')
    save_dataframe_to_silver(df_name, 'name_basics')

fix_name_basics(dataframes['name_basics'])

# COMMAND ----------

def fix_title_akas(df):
    df = df.na.replace("\\N", None)
    df = column_names_camel_to_snake_case(df)
    df = df.drop('is_original_title')
    df = df.withColumn('ordering', col('ordering').cast('int'))
    display(df)
    save_dataframe_to_silver(df, 'title_akas')

fix_title_akas(dataframes['title_akas'])

# COMMAND ----------

def fix_title_basics(df):
    df = df.na.replace("\\N", None)
    df = column_names_camel_to_snake_case(df)
    df = df.withColumn('is_adult', col('is_adult').cast('boolean'))
    df = df.withColumn('start_year', col('start_year').cast('int'))
    df = df.withColumn('end_year', col('end_year').cast('int'))
    df = df.withColumn('runtime_minutes', col('runtime_minutes').cast('int'))

    df_genres = df.select('tconst', 'genres').withColumn('genres', explode(split(col('genres'), ',')))
    df = df.drop('genres')
    display(df_genres)
    save_dataframe_to_silver(df_genres, 'title_genres')
    display(df)
    save_dataframe_to_silver(df, 'title_basics')

fix_title_basics(dataframes['title_basics'])

# COMMAND ----------

def fix_title_ratings(df):
    df = df.na.replace("\\N", None)
    df = column_names_camel_to_snake_case(df)
    df = df.withColumn('average_rating', col('average_rating').cast('decimal(3,1)'))
    df = df.withColumn('num_votes', col('num_votes').cast('int'))
    display(df)

    save_dataframe_to_silver(df, 'title_ratings')

fix_title_ratings(dataframes['title_ratings'])

# COMMAND ----------

def fix_title_principals(df):
    df = df.na.replace("\\N", None)
    df = column_names_camel_to_snake_case(df)

    df = df.withColumn('ordering', col('ordering').cast('int'))
    df = df.withColumn('characters', regexp_replace(col('characters'), r'^\[|\]$', ''))
    # df = df.withColumn('characters', regexp_replace(col('characters'), r'^"|"$', ''))


    display(df)

    save_dataframe_to_silver(df, 'title_principals')

fix_title_principals(dataframes['title_principals'])