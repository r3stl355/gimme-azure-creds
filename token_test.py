# Databricks notebook source
# DBTITLE 1,Load the tokens
# MAGIC %run ./token

# COMMAND ----------

# DBTITLE 1,Tokens are available for use to make API calls or JDBC connections 
print(f'ACCESS_TOKEN={ACCESS_TOKEN}\n\nREFRESH_TOKEN={REFRESH_TOKEN}')
