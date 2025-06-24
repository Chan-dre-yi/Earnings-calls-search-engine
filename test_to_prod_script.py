# USED TO COPY DATA FROM ONE DB SITE TO ANOTHER
from pymongo import MongoClient

# MongoDB connection strings
source_connection_string = "" #source db connection string
destination_connection_string = "" #destination db connection string

# Database and collection details
source_db_name = ""
source_collection_name = ""
destination_db_name = ""
destination_collection_name = ""

# Connect to the source MongoDB
source_client = MongoClient(source_connection_string)
source_db = source_client.get_default_database()
source_collection = source_db[source_collection_name]

# Connect to the destination MongoDB
destination_client = MongoClient(destination_connection_string)
destination_db = destination_client.get_default_database()
destination_collection = destination_db[destination_collection_name]

try:
    # Fetch all documents from the source collection
    documents = list(source_collection.find())
    print(f"Fetched {len(documents)} documents from the source collection.")

    if documents:
        # Insert documents into the destination collection
        result = destination_collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} documents into the destination collection.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the MongoDB connections
    source_client.close()
    destination_client.close()
