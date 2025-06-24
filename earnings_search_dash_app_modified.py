'''
Dash:
http://127.0.0.1:8050/
'''

import pandas as pd
from pymongo import MongoClient
import re
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from datetime import datetime
from nltk.corpus import wordnet as wn
import re
import db_connection as mgDB

# Inputs
context_sizes = [1, 2, 3]
default_context_size = 3
default_keywords = 'intel or silicon photonics'
MONGO_URI = mgDB.MONGO_URI
MONGO_URI_US = mgDB.MONGO_URI_US

EarningsCallCollection = 'Financial_Batch_Earnings_Call'


# Global variable for the database connection
client = None
db = None

def connect_to_db(site):
    global client, db
    if site == 'INDIA':
        client = MongoClient(MONGO_URI)
    elif site == 'US':
        client = MongoClient(MONGO_URI_US)
    db = client.get_default_database()

# Initialize the default connection
connect_to_db('INDIA')

db_india = MongoClient(MONGO_URI)['TDAP_DB']
db_us = MongoClient(MONGO_URI_US)['TDAP_DB_US']
db_list = [db_india, db_us]

# Global variables to track the task state
running = False
c = "not cancelled"

def get_db():
    return db

def check_cancel_for_FetchData():
    global running, c
    if not c=="cancelled" and not running: print("Cancel was pressed.", datetime.today().strftime("%H:%M:%S")); c = "cancelled"; return pd.DataFrame()

def fetch_data(query, db_list, keywords):
    """
    Fetch data from the database with synonym expansion for given keywords.
    :param query: Original user query.
    :param db_list: List of database connections.
    :param keywords: List of keywords to include in the search.
    :return: DataFrame containing fetched data.
    """
    print("Fetching data from database...", datetime.today().strftime("%H:%M:%S"))
    check_cancel_for_FetchData()
    earnings_call = db_list[0]['Financial_Batch_Earnings_Call']
    earnings_call.create_index([("doc_text", "text")])
    check_cancel_for_FetchData()

    # Generate the final query with synonyms based on the input query
    final_query = construct_search_query(query, db_list)

    # print(f"Search query: {final_query}")
    check_cancel_for_FetchData()

    # Perform the search with sorting and limiting results
    earnings_call_data = earnings_call.find(
        {"$text": {"$search": final_query}},
        {"score": {"$meta": "textScore"}}  # Include relevance score in results
    ).sort(
        [("score", {"$meta": "textScore"}), ("doc_date", -1)]  # Sort by relevance and recency
    ).limit(50)  # Limit to top 50 results

    print({"$text": {"$search": final_query}})
    check_cancel_for_FetchData()

    # Convert the result to a DataFrame
    df = pd.DataFrame(list(earnings_call_data))

    print("Data fetched successfully.", datetime.today().strftime("%H:%M:%S"))
    return df

def construct_search_query(query, db_list):
    """
    Constructs the final search query by including synonyms for terms in the query.

    :param query: Original user query.
    :param db_list: List of database connections.
    :return: String representing the search query.
    """
    syn_collection = db_list[0]['Synonyms_List']

    # Handle AND and OR queries in the query variable
    if " and " in query.lower():
        # Replace "and" with space for AND query
        search_query = ' '.join(f"\"{word.strip()}\"" for word in query.split(" and "))
    elif " or " in query.lower():
        # Replace "or" with "|" for OR query
        search_query = ' | '.join(word.strip() for word in query.split(" or "))
    else:
        # Default to the original query
        search_query = query

    # Extract keywords from the search_query
    keywords = [word.strip().strip('"') for word in search_query.split('|') if word.strip()]
    synonym_mapping = get_or_generate_synonyms(keywords, syn_collection)

    # Maintain the order of keywords and their synonyms
    query_terms = []
    for keyword in keywords:
        all_terms = synonym_mapping.get(keyword, [keyword])
        # Add each term as a quoted string to avoid splitting
        query_terms.extend([f'{term}' for term in all_terms])
    # print(query_terms)
    # Join terms with '|' separator for the final query

    return " | ".join(query_terms)

def get_or_generate_synonyms(keywords, syn_list):
    """
    Fetch or generate synonyms for a list of keywords, handling compound terms like "Artificial Intelligence/AI".

    :param keywords: List of keywords to process.
    :param syn_list: MongoDB collection for storing/retrieving synonyms.
    :return: Dictionary mapping keywords to their synonyms.
    """
    result = {}

    for word in keywords:
        # Perform a case-insensitive search in MongoDB collection
        syn_data = syn_list.find_one({"Word": {"$regex": f"\\b{word}\\b", "$options": "i"}})

        if syn_data:
            # If found, retrieve synonyms
            synonyms = syn_data['Synonyms'].split(", ")

            # Handle compound terms in the "Word" field
            compound_terms = syn_data['Word'].split('/')
            if len(compound_terms) > 1:
                # Add alternate terms from the compound word (excluding the original keyword)
                alternate_term = next(
                    (term.strip() for term in compound_terms if term.strip().lower() != word.lower()), None
                )
                if alternate_term:
                    synonyms.insert(0, alternate_term)

            print(f"Retrieved synonyms for '{word}' from MongoDB: {synonyms}")
        else:
            # If not found, generate synonyms using WordNet
            synonyms = generate_synonyms_with_wordnet(word)
            print(f"Generated synonyms for '{word}' using WordNet: {synonyms}")

            # Insert the keyword and its synonyms into MongoDB
            syn_list.insert_one({"Word": word, "Synonyms": ", ".join(synonyms)})
            print(f"Inserted synonyms for '{word}' into MongoDB.")

        # Include the keyword itself in the result
        result[word] = [word] + synonyms

    return result

def generate_synonyms_with_wordnet(word, num_synonyms=5):
    """
    Generate synonyms for a given word using WordNet.
    """
    synonyms = set()
    for synset in wn.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name().replace('_', ' '))
            if len(synonyms) >= num_synonyms:
                break
        if len(synonyms) >= num_synonyms:
            break
    return list(synonyms)


def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    # Replace hyphens or similar punctuation between words with a space
    text = re.sub(r'(?<=\w)[-](?=\w)', ' ', text)
    text = text.replace('\n', '')  # Remove '\n'
    # Remove any other extraneous whitespace, keeping text clean
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_sentences_with_speaker(doc_text, keyword, context_size):
    # Regex patterns for keyword and speaker detection
    keyword_pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
    speaker_pattern = re.compile(r'^([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+):')

    # Split document text into sentences and identify speakers
    sentences = re.findall(r'([^.?!]*[.?!])', doc_text)
    sentence_with_speakers = []
    current_speaker = None

    # Associate each sentence with its speaker
    for sentence in sentences:
        speaker_match = speaker_pattern.match(sentence.strip())
        if speaker_match:
            current_speaker = speaker_match.group(1)
        sentence_with_speakers.append((current_speaker, sentence.strip()))

    matched_sentences = []
    previous_speaker = None
    seen_sentences = set()  # Set to track seen sentences

    # Gather context sentences around keyword occurrences
    for i, (speaker, sentence) in enumerate(sentence_with_speakers):
        if keyword_pattern.search(sentence):
            # Define context range
            start = max(0, i - context_size)
            end = min(len(sentence_with_speakers), i + context_size + 1)

            for j in range(start, end):
                context_speaker, context_sentence = sentence_with_speakers[j]
                # Avoid repeating the speaker's name
                if context_speaker and context_speaker != previous_speaker:
                    if not context_sentence.startswith(f"{context_speaker}:"):
                        formatted_sentence = f"{context_speaker}: {context_sentence}"
                    else:
                        formatted_sentence = context_sentence

                    # Only add unique sentences
                    if formatted_sentence not in seen_sentences:
                        matched_sentences.append(formatted_sentence)
                        seen_sentences.add(formatted_sentence)

                elif context_speaker == previous_speaker:
                    if context_sentence not in seen_sentences:
                        matched_sentences.append(context_sentence)
                        seen_sentences.add(context_sentence)

                # Update previous speaker for the next iteration
                previous_speaker = context_speaker

    return matched_sentences

def format_results(company_name, doc_date, extracted_text, load_date, keyword):
    # Convert doc_date to string if it's a Timestamp
    if isinstance(doc_date, pd.Timestamp) or isinstance(load_date, pd.Timestamp):
        doc_date = doc_date.strftime('%Y-%m-%d')
        load_date = load_date.strftime('%Y-%m-%d')
    else:
        doc_date = str(doc_date)
        load_date = str(load_date)

    # Join the extracted sentences into a single string
    extracted_text_combined = ''.join(extracted_text).strip()
    result = {
        "company_name": company_name,
        "doc_date": doc_date,
        "extracted_text": extracted_text_combined,
        "load_date": load_date
    }
    return result

def keyword_matching_with_dataframe(df, keyword, context_size):
    '''
    Finds relevant sentences around the given keyword
    '''
    results_list = []
    keyword_pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)

    for index, row in df.iterrows():
        company_name = row.get('company_name', 'Unknown Company')
        doc_date = row.get('doc_date', 'Unknown Date')
        doc_text_pr = row.get('doc_text_pr', "")
        doc_text_qa = row.get('doc_text_qa', "")
        load_date = row.get('load_date', 'Unknown Date')

        if 'Intel Co' not in company_name:
            # Extract sentences containing the keyword from remarks and Q&A separately
            extracted_pr = extract_sentences_with_speaker(clean_text(doc_text_pr), keyword, context_size) if doc_text_pr else []
            extracted_qa = extract_sentences_with_speaker(clean_text(doc_text_qa), keyword, context_size) if doc_text_qa else []

            # If matching sentences are found in either section, process further
            if extracted_pr or extracted_qa:
                formatted_result = {
                    "company_name": company_name,
                    "doc_date": str(doc_date),
                    "prepared_remarks": " ".join(extracted_pr).strip() if extracted_pr else None,
                    "qa": " ".join(extracted_qa).strip() if extracted_qa else None,
                    "load_date": str(load_date)
                }
                results_list.append(formatted_result)

    # Create DataFrame with separate Remarks and Q&A columns
    results_df = pd.DataFrame(results_list)
    if results_df.empty:
        return results_df

    results_df['keyword_count'] = results_df['prepared_remarks'].apply(lambda text: len(re.findall(keyword_pattern, text)) if text else 0) + \
                                  results_df['qa'].apply(lambda text: len(re.findall(keyword_pattern, text)) if text else 0)
    results_df['keyword'] = keyword
    results_df['context_size'] = context_size

    # Remove duplicates based on company_name and doc_date
    results_df = results_df.drop_duplicates(subset=['company_name', 'doc_date'], keep='first')
    # Sort the DataFrame by keyword_count, company_name, and doc_date
    results_df = results_df.sort_values(by=['company_name', 'doc_date', 'keyword_count'], ascending=[True, True, False])

    return results_df

def check_cancel_for_UpdateOutput():
    global running
    if not running: running = False; print("Cancel was pressed.", datetime.today().strftime("%H:%M:%S")); return [], "Task was canceled."




# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(style={'padding': '80px'}, children=[
    html.H1(
        "Earnings Calls Search Engine",
        style={
            'fontSize': '48px',
            'textAlign': 'center',
            'marginTop': '-40px'  # Moves the heading upwards
        }
    ),
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'paddingBottom': '20px'}, children=[
        html.Div(),
        html.Div(children=[
            html.Label("DB Site:", style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='db-site-dropdown',
                options=[
                    {'label': 'India', 'value': 'INDIA'},
                    {'label': 'US', 'value': 'US'}
                ],
                value='INDIA',  # Default selection
                clearable=False,
                style={'width': '200px'}
            )
        ])
    ]),
    html.Div(style={'padding': '40px', 'backgroundColor': '#f0f0f0', 'borderRadius': '30px'}, children=[
        html.Label("Search for:"),
        dcc.Input(
            id='keyword-input',
            #value=', '.join(keywords),
            value=default_keywords,
            style={'width': '65%', 'maxWidth': '1200px', 'height': '25px', 'marginRight': '10px', 'marginLeft': '10px'}
        ),
        html.Div("Enter keywords or phrases. Use or/and for grouping. Example: fish or chips and corns.", style={'fontSize': '10px', 'color': '#888', 'marginTop': '3px', 'marginLeft': '80px', 'fontFamily': 'Open Sans, Arial, sans-serif'}),
        html.Div(style={'height': '15px'}),
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            html.Label("Context:", style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='context-size-dropdown',
                options=[{'label': str(size), 'value': size} for size in context_sizes],
                value=default_context_size,
                clearable=False,
                placeholder="Select a context size",
                style={'width': '350px', 'marginRight': '20px', 'marginLeft': '7px'}
            ),
        ]),
        html.Div("Select how many sentences to include around the keywords for context.", style={'fontSize': '10px', 'color': '#888', 'marginTop': '3px', 'marginLeft': '80px', 'fontFamily': 'Open Sans, Arial, sans-serif'}),
        html.Div(style={'height': '15px'}),
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            html.Label("Sort by:", style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='sort-dropdown',
                options=[
                    {'label': 'Keyword Count', 'value': 'keyword_count'},
                    {'label': 'Most Recent', 'value': 'recent_to_old'},
                    {'label': 'Company Name', 'value': 'company_name'}
                ],
                value='keyword_count',
                clearable=False,
                style={'width': '350px', 'marginLeft': '8px'}
            ),
        ]),
        html.Div("Choose how you would like the results to be sorted.", style={'fontSize': '10px', 'color': '#888', 'marginTop': '3px', 'marginLeft': '80px', 'fontFamily': 'Open Sans, Arial, sans-serif'}),
        html.Div(style={'height': '15px'}),
        html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
            html.Button(
                'Go', 
                id='update-button', 
                n_clicks=0,
                style={
                    'fontSize': '16px',
                    'padding': '10px 30px',
                    'marginLeft': '10px',
                    'backgroundColor': '#4B4B4B',
                    'color': 'white',
                    'border': 'none',
                    'fontWeight': 'bold',
                    'cursor': 'pointer',
                    'borderRadius': '12px',
                }
            ),
            html.Button(
                'Cancel', 
                id='cancel-button', 
                n_clicks=0,
                style={
                    'fontSize': '16px',
                    'padding': '10px 30px',
                    'marginLeft': '10px',
                    'backgroundColor': '#c0c0c0',
                    'color': '#333',
                    'border': 'none',
                    'fontWeight': 'bold',
                    'cursor': 'pointer',
                    'borderRadius': '12px',
                }
            ),
        ])
    ]),
    html.Div(style={'height': '60px'}),
    
    html.Div(
        id='output-container',
        style={
            'padding': '40px',
            'backgroundColor': '#FAF3E0',
            'borderRadius': '30px',
            'boxShadow': '0 16px 32px rgba(0, 0, 0, 0.2)'
        },
        children=[
            dcc.Loading(
                id="loading",
                type="dot",
                style={'color': '#F5F5DC'},
                children=[
                    html.Div(id='loading-output', style={'padding': '20px', 'textAlign': 'center', 'color': '#333'})
                ]
            ),
            html.Div(id='results-output')
        ]
    )
])

@app.callback(
    [Output('results-output', 'children'),
     Output('loading-output', 'children')],
    [Input('update-button', 'n_clicks'),
     Input('cancel-button', 'n_clicks'),
     Input('db-site-dropdown', 'value')],  # Add site dropdown as an input
    [State('keyword-input', 'value'),
     State('context-size-dropdown', 'value'),
     State('sort-dropdown', 'value')]
)

def update_output(go_clicks, cancel_clicks, site, keyword_input, selected_context_size, sort_by):
    global running
    if running:
        return [], "A task is already running. Please wait or cancel."

    if go_clicks > 0:
        running = True
        # Update the database connection
        connect_to_db(site)

        # Process keywords
        new_keywords = [kw.strip() for kw in keyword_input.replace('and', ',').replace('or', ',').split(',')]
        db_list = [db_india, db_us]  # Example: Ensure to initialize these earlier
        df = fetch_data(keyword_input, db_list, new_keywords)

        if df.empty:
            running = False
            return [], "No data found for the provided keywords."

        merged_df = pd.DataFrame()
        for keyword in new_keywords:
            check_cancel_for_UpdateOutput()
            result_df = keyword_matching_with_dataframe(df, keyword, selected_context_size)
            merged_df = pd.concat([merged_df, result_df], ignore_index=True)

        check_cancel_for_UpdateOutput()

        if merged_df.empty:
            running = False
            return [], "No results found."

        # Sorting and formatting results
        if sort_by == 'keyword_count':
            merged_df = merged_df.sort_values(by='keyword_count', ascending=False)
        elif sort_by == 'recent_to_old':
            merged_df = merged_df.sort_values(by='doc_date', ascending=False)
        elif sort_by == 'company_name':
            merged_df = merged_df.sort_values(by='company_name')

        # Format results for display
        newspaper_format = []
        newspaper_format.append(html.H2("Earnings Calls Search Report", style={'fontSize': '48px', 'textAlign': 'center', 'marginBottom': '60px', 'color': '#333'}))

        for company in merged_df['company_name'].unique():
            company_data = merged_df[merged_df['company_name'] == company]
            newspaper_format.append(html.H3(company, style={'fontSize': '24px', 'color': '#333', 'marginBottom': '10px'}))

            for _, row in company_data.iterrows():
                newspaper_format.append(html.H4(row['doc_date'], style={'fontSize': '18px', 'color': '#555'}))
                # Prepared Remarks
                prepared_text = row['prepared_remarks'] if pd.notna(row['prepared_remarks']) else ""
                if prepared_text:
                    newspaper_format.append(html.H5("Prepared Remarks:", style={'fontSize': '14px', 'color': '#777'}))
                    newspaper_format.append(html.P(prepared_text, style={'fontSize': '16px', 'color': '#333'}))
                # Q&A
                qa_text = row['qa'] if pd.notna(row['qa']) else ""
                if qa_text:
                    newspaper_format.append(html.H5("Q&A:", style={'fontSize': '14px', 'color': '#777'}))
                    newspaper_format.append(html.P(qa_text, style={'fontSize': '16px', 'color': '#333'}))

        running = False
        return newspaper_format, ""

    if cancel_clicks > 0:
        running = False
        return [], "Hit the 'Go' button to see the report."

    return [], "No action yet."


if __name__ == '__main__':
    app.run(debug=True)
