import os
import pandas as pd
import json
import db_connection as mgDB

# Set proxy configurations for downloading nltk data
os.environ['https_proxy'] = ''
os.environ['no_proxy'] = ''

# Load the JSON data
with open('syn_ant_sent_sim.json', 'r') as f:
    data = json.load(f)

# Initialize lists to hold words and synonyms for the DataFrame
words = []
synonyms_list = []

# Process each entry in data
for entry in data:
    word = entry['word']
    # Check if 'syn_list' exists in the entry and extract synonyms if available
    if 'syn_list' in entry:
        synonyms = ', '.join([syn['synonym'] for syn in entry['syn_list']])
    else:
        synonyms = ""
    words.append(word)
    synonyms_list.append(synonyms)

# Create a DataFrame from the lists
df1 = pd.DataFrame({
    'Word': words,
    'Synonyms': synonyms_list
})

# Step 1: Load JSON data from file
with open('technical_terms.json', 'r') as file:
    data = json.load(file)

# Step 2: Convert JSON data to a DataFrame
df = pd.DataFrame(data)

# Step 1: Load JSON data from file
with open('NonTechnicalTerms.json', 'r') as file:
    data = json.load(file)

# Step 2: Convert JSON data to a DataFrame
df2 = pd.DataFrame(data)

# Drop duplicates based on the "Word" column, keeping only the first occurrence
df = df.drop_duplicates(subset="Word", keep="first")
df2 = df2.drop_duplicates(subset="term", keep="first")

# Standardize column names to 'Word' and 'Synonyms'
df.columns = ['Word', 'Synonyms']
df1.columns = ['Word', 'Synonyms']
df2.columns = ['Word', 'Synonyms']

# Concatenate the three DataFrames
combined_df = pd.concat([df, df1,df2], ignore_index=True)

# Drop duplicates based on the "Word" column, keeping only the first occurrence
combined_df = combined_df.drop_duplicates(subset="Word", keep="first")

from pymongo import MongoClient

MONGO_URI = mgDB.MONGO_URI
MONGO_URI_US = mgDB.MONGO_URI_US

# Set Collection to use
syn_list = 'Synonyms_List'

####################
# DB CONNECTOR
####################
# MongoDB connector
def db_connector():
    client = MongoClient(MONGO_URI)
    client2 = MongoClient(MONGO_URI_US)
    db = client.get_default_database()  # This will connect to the database specified in the URI
    db2 = client2.get_default_database() 
    # print("Connected to db.")
    return db,db2

db, db2 = db_connector()

# Convert DataFrame to list of dictionaries
df2_dict = combined_df.to_dict("records")

# Insert records with duplication check
for record in df2_dict:
    word = record['Word']
    
    # Insert into first database
    db[syn_list].update_one(
        {'Word': word},      # Search criteria
        {'$setOnInsert': record},  # Insert only if not present
        upsert=True          # If not present, insert
    )
    
    # Insert into second database
    db2[syn_list].update_one(
        {'Word': word},
        {'$setOnInsert': record},
        upsert=True
    )

print("Data inserted successfully (duplicates ignored)!")


