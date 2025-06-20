'''
Deletes older updates first.
Then It looks through the text to find out where the Q&A starts.
It does this by looking for the word "question."
If it sees "question," it checks a few sentences after that to see if "question" appears again.
If it does, it starts collecting all the following sentences as Q&A; if not, it keeps adding sentences to the prepared remarks.
In the end, you get a clear split of what was said before the Q&A and what was part of the Q&A.
'''



from pymongo import MongoClient
import re

MONGO_URI = ""
# EarningsCallCollection = 'ChandreyiFMP_BatchEarningsCall'
EarningsCallCollection = 'Financial_Batch_Earnings_Call'

client = MongoClient(MONGO_URI)
db = client.get_default_database()
collection = db[EarningsCallCollection]




###########################
# Delete doc_text_pr and doc_text_qa from all documents in one go
result = collection.update_many(
    {},
    {'$unset': {'doc_text_pr': "", 'doc_text_qa': ""}}
)

print(f"Deletion completed successfully! Modified count: {result.modified_count}")
############################




################
# Define the number of sentences to check for the next 'question' occurance
n = 3
################


def segment_transcripts(doc_text):
    # Split into sentences based on punctuation
    sentences = re.split(r'(?<=[.!?]) +', doc_text)
    
    prepared_remarks = []
    qa_section = []
    q_and_a_started = False  # Flag to indicate if Q&A has started

    for i, sentence in enumerate(sentences):
        if re.search(r'\bquestion\b', sentence, re.IGNORECASE):
            # Check the next three sentences for the word "question"
            if i < len(sentences) - 1:
                next_sentences = sentences[i+1:i+n]  # Get the next n sentences
            else:
                next_sentences = sentences[i+1:]  # Get the remaining sentences if less than three

            if any(re.search(r'\bquestion\b', next_sentence, re.IGNORECASE) for next_sentence in next_sentences):
                q_and_a_started = True  # Confirm Q&A has started

        if not q_and_a_started:
            prepared_remarks.append(sentence)  # Add to prepared remarks
        else:
            qa_section.append(sentence)  # Add to Q&A section

    return {
        "doc_text_pr": ' '.join(prepared_remarks),  
        "doc_text_qa": ' '.join(qa_section)
    }





# Will take an hour or more
#########################
# Fetch all documents from the collection
documents = list(collection.find())

# Process each document to segment text
for document in documents:
    if 'doc_text' in document:  # Ensure doc_text exists
        print("here")
        doc_text = document['doc_text']
        segments = segment_transcripts(doc_text)

        # Print the details to be stored
        # print(f"Document ID: {document['_id']}")
        # print(f"Prepared Remarks (doc_text_pr): {segments['doc_text_pr']}")
        # print(f"Q&A Section (doc_text_qa): {segments['doc_text_qa']}")
        # print("-" * 40)  # Separator for readability

        # Update the document with new fields (commented out for now)
        collection.update_one(
            {'_id': document['_id']},
            {'$set': segments}
        )
##########################