from datetime import datetime, timedelta,date
import time
import os
import sys
import argparse
import requests
import configparser
import string
import json
from ssl import create_default_context
import pandas as pd
import math
from pymongo import MongoClient
import logging
import traceback
from pymongo.errors import DuplicateKeyError
import requests
from datetime import datetime
from bson import ObjectId

## This code is used to load dockerhub Repositories
# Set Proxy variables
os.environ["http_proxy"] = " " #set proxy

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# MongoDB connection string
MONGO_URI = " " #your mongo db connection string
api_key = '' #your api key

# Global variable to store the current collection name
current_collection = None

# MongoDB connector
def db_connector():
    try:
        logging.info(f"Connecting to MongoDB with URI: {MONGO_URI}")
        client = MongoClient(MONGO_URI)
        db = client.get_default_database()
        logging.info("Connected to db.")
        return db
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {str(e)}\n{traceback.format_exc()}")
        raise

# Function to log updates and errors to MongoDB
def log_update(symbol, exchange, collection_name, log_collection_name, error_message=None):
    db = db_connector()
    load_date = datetime.now()
    log_id = f"{symbol}_{exchange}_{load_date.strftime('%Y%m')}_{collection_name}"
    log_record = {
        '_id': log_id,
        'symbol': symbol,
        'exchange': exchange,
        'load_date': load_date,
        'collection_name': collection_name,
        'error_message': error_message  # Store error message if provided
    }
    try:
        result = db[log_collection_name].insert_one(log_record)
        logging.info(f"Logged update with _id: {result.inserted_id}")
    except DuplicateKeyError:
        logging.warning(f"Log entry for {symbol} {exchange} in {collection_name} on {load_date.strftime('%Y-%m-%d')} already exists.")
        if error_message:  # Exit only if this is an error
            sys.exit()

# Function to insert records into MongoDB
def insert_records(collection_name, records):
    global current_collection
    current_collection = collection_name
    db = db_connector()
    collection = db[collection_name]
    
    try:
        if isinstance(records, list):
            for record in records:
                unique_field_value = record.get('_id')
                result = collection.update_one(
                    {'_id': unique_field_value},
                    {'$set': record},
                    upsert=True
                )
                if result.upserted_id:
                    logging.info(f"Inserted new record with _id: {result.upserted_id} into {collection_name}")
                else:
                    logging.info(f"Updated record with _id: {unique_field_value} in {collection_name}")
        else:
            unique_field_value = records.get('_id')
            result = collection.update_one(
                {'_id': unique_field_value},
                {'$set': records},
                upsert=True
            )
            if result.upserted_id:
                logging.info(f"Inserted new record with _id: {result.upserted_id} into {collection_name}")
            else:
                logging.info(f"Updated record with _id: {unique_field_value} in {collection_name}")
    except Exception as e:
        error_message = f"An error occurred while inserting records: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_message)
        log_update("N/A", "N/A", collection_name, "FMP_LogCollection", error_message)  # Log error with placeholder values

def get_company_profile_data(company):
    print(f'processing company profile data :{company}')
    # api_key = ''
    company_profile_url = f'https://financialmodelingprep.com/api/v4/company-outlook?symbol={company}&apikey={api_key}'
    response = requests.get(company_profile_url)
    result_json = response.json()
    company_dic = {}
    record = []
    company_dic['symbol'] = result_json['profile']['symbol']
    company_dic['companyName'] = result_json['profile']['companyName']
    company_dic['currency'] = result_json['profile']['currency']
    company_dic['cik'] = result_json['profile']['cik']
    company_dic['isin'] = result_json['profile']['isin']
    company_dic['cusip'] = result_json['profile']['cusip']
    company_dic['exchange'] = result_json['profile']['exchange']
    company_dic['exchangeShortName'] = result_json['profile']['exchangeShortName']
    company_dic['industry'] = result_json['profile']['industry']
    company_dic['website'] = result_json['profile']['website']
    company_dic['description'] = result_json['profile']['description']
    company_dic['ceo'] = result_json['profile']['ceo']
    company_dic['fullTimeEmployees'] = result_json['profile']['fullTimeEmployees']    
    company_dic['sector'] = result_json['profile']['sector']
    company_dic['country'] = result_json['profile']['country']
    company_dic['phone'] = result_json['profile']['phone']
    company_dic['address'] = result_json['profile']['address']
    company_dic['city'] = result_json['profile']['city']
    company_dic['state'] = result_json['profile']['state']
    company_dic['zip'] = result_json['profile']['zip']
    company_dic['ipoDate'] = result_json['profile']['ipoDate']
    company_dic['executives'] = result_json['keyExecutives']
    company_dic['_id'] = company_dic['symbol']
    company_dic['_index'] = 'tdap_financial_company_details'
    company_dic['doc_date'] = company_dic['ipoDate']
    company_dic['load_date'] = datetime.today()
    record.append(company_dic)
    if len(record) > 0:
        insert_records('Financial_Company_Profile', record)
        time.sleep(2)
        print(f'Finished processing profile  for company :{company}')
        
   

def get_earning_transcript_historical(company, company_name, exchange_name, start_year, end_year):    
    print(f'processing finacial transcript for company :{company}')
    # api_key = ''
    for year in range (start_year,end_year):
        #income statement
        transcript_url = f'https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{company}?year={year}&apikey={api_key}'
        response_transcript = requests.get(transcript_url)
        transcript_lists = response_transcript.json()
        
        record = []        
        for item in transcript_lists:  
            data = {}              
            data['_index'] = 'tdap_financial_transcript_ver1'
            data['symbol'] = item['symbol']
            data['year'] = item['year']
            data['quarter'] = item['quarter']
            data['_id'] = item['symbol'] + "_" + str(item['quarter']) + "_" + str(item['year'])
            data['doc_date'] =datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S')
            data['doc_text'] = item['content']
            data['load_date'] = datetime.today()
            data['doc_type'] = "financial_transcript"
            data['company_name'] = company_name
            data['exchange'] = exchange_name
            record.append(data)
        if len(record) > 0:
            # res=helpers.bulk(es_client,record)
            insert_records('Financial_Batch_Earnings_Call', record)
            print(f'Finished processing transcript  for company :{company} yeear {year}')
            # print(f'number of records inserted :{res}')

def get_financial_10q_data(company, company_name, exchange_name):
    
    print(f'processing finacial statment (10Q) for company :{company}')
    # api_key = ''
    #income statement
    income_url = f'https://financialmodelingprep.com/api/v3/income-statement/{company}?period=annual&limit=4&apikey={api_key}'
    response_income = requests.get(income_url)
    annual_income_statement_lists = response_income.json()
    balance_sheet_url = f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?period=annual&limit=4&apikey={api_key}'
    response_balance = requests.get(balance_sheet_url)
    balance_lists = response_balance.json()
    cash_flow_url = f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{company}?period=annual&limit=4&apikey={api_key}'
    response_cashflow = requests.get(cash_flow_url)
    cashflow_lists = response_cashflow.json()
    iter_count = min(len(annual_income_statement_lists), len(balance_lists), len(cashflow_lists))
    record = []
    count = 0
    while count < iter_count:
        merged_result = {**annual_income_statement_lists[count], **balance_lists[count], **cashflow_lists[count]}
        merged_result['_index'] = 'tdap_financial_10q'
        merged_result['_id'] = merged_result['symbol'] + "_" + str(merged_result['fillingDate'])
        merged_result['load_date'] = datetime.today()
        if merged_result['fillingDate'] == '':
            merged_result['fillingDate'] = merged_result['date']
        merged_result['doc_date'] = merged_result['fillingDate']
        merged_result['doc_type'] = "financial_10q"
        merged_result['year_quarter'] = str(merged_result['calendarYear']) + "." + str(merged_result["period"])
        merged_result['company_name'] = company_name
        merged_result['exchange'] = exchange_name
        
        record.append(merged_result)
        count += 1
    #print(response.status_code)
    if len(record) > 0:
        # res=helpers.bulk(es_client,record)
        # print(f'number of records inserted :{res}')
        insert_records('Financial_10Q', record)
    print(f'Finished processing finacial statment (10Q) for company :{company}')

# Function to fetch financial 10-K data
def get_financial_10k_data(company, company_name, exchange_name):
    global current_collection
    current_collection = 'financial_10k'
    logging.info(f'Processing financial statement (10K) for company: {company}')
    try:
        api_key = 'HiP0DDOkZWsTjqkXKnpxDZjxD1dDrbCM'
        income_url = f'https://financialmodelingprep.com/api/v3/income-statement/{company}?limit=2&apikey={api_key}'
        response_income = requests.get(income_url)
        annual_income_statement_lists = response_income.json()

        balance_sheet_url = f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?limit=2&apikey={api_key}'
        response_balance = requests.get(balance_sheet_url)
        balance_lists = response_balance.json()

        cash_flow_url = f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{company}?limit=2&apikey={api_key}'
        response_cashflow = requests.get(cash_flow_url)
        cashflow_lists = response_cashflow.json()

        iter_count = min(len(annual_income_statement_lists), len(balance_lists), len(cashflow_lists))
        records = []
        for count in range(iter_count):
            merged_result = {**annual_income_statement_lists[count], **balance_lists[count], **cashflow_lists[count]}
            merged_result['_index'] = 'tdap_financial_10k'
            merged_result['_id'] = f"{merged_result['symbol']}_{merged_result['fillingDate']}"
            merged_result['load_date'] = datetime.today()
            merged_result['doc_date'] = merged_result['fillingDate']
            merged_result['doc_type'] = "financial_10k"
            merged_result['company_name'] = company_name
            merged_result['exchange'] = exchange_name
            records.append(merged_result)

        if records:
            insert_records('financial_10k', records)
            log_update(company, exchange_name, 'financial_10k', 'ChandreyiFMP_LogCollection')
        logging.info(f'Finished processing financial statement (10K) for company: {company}')
    except Exception as e:
        error_message = f"An error occurred while processing financial data for {company}: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_message)
        log_update(company, exchange_name, current_collection, 'ChandreyiFMP_LogCollection', error_message)


def get_tickers(exchange_name):
    # api_key=''
    # api_key = 'HiP0DDOkZWsTjqkXKnpxDZjxD1dDrbCM'
    ticker_url = f'https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}'
    responsee = requests.get(ticker_url)
    ticker_list = responsee.json()
    print('Total no of tickers {}'.format(len(ticker_list)))
    df_ticker = pd.DataFrame(ticker_list)
    df_ticker = df_ticker[df_ticker['exchangeShortName'] == exchange_name]
    df_ticker = df_ticker.sort_values('symbol')
    df_ticker = df_ticker.reset_index()    
    print('No of tickers {} for excahnge {}'.format(df_ticker.shape[0], exchange_name))
    return df_ticker

def get_company_finacial_by_segment(company, company_name,exchange_name):
    flag = 'F' #I- Incremental F- Full
    print(f'processing finacial segments for company :{company}')
    # api_key = ''
    #annual
    url = f'https://financialmodelingprep.com/api/v4/revenue-product-segmentation?symbol={company}&structure=flat&apikey={api_key}&period=quarter'
    responsee = requests.get(url)
    segments_details = responsee.json()  
    record = []    
    count = 0    
    for item in segments_details: 
        for key in item.keys():             
             for segment in item[key]:
                count += 1
                data={}
                data['doc_date'] = datetime.strptime(key, '%Y-%m-%d')
                data['_index'] = 'tdap_financial_company_segments'
                data['symbol'] = company
                data['segment_name'] = segment
                data['segment_value'] = item[key][segment]
                data['year'] = key.split('-')[0].strip()                
                data['_id'] = company + '_' + key + '_'+segment.lower().replace(' ','_')
                data['load_date'] = datetime.today()
                data['doc_type'] = "financial_company_segments"
                data['company_name'] = company_name
                data['exchange'] = exchange_name
                if flag == 'I' and count >= 4:
                    break
                record.append(data)
    if len(record) > 0:
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing finacial segments for company :{company}')
        # print(f'number of records inserted :{res}')
        insert_records('Financial_Product_Segmentation', record)

def get_company_finacial_by_geographies(company, company_name,exchange_name):
    flag = 'I' #I- Incremental F- Full
    print(f'processing finacial segments for company :{company}')
    #annual    
    url = f'https://financialmodelingprep.com/api/v4/revenue-geographic-segmentation?symbol={company}&structure=flat&apikey={api_key}&period=quarter'
    responsee = requests.get(url)
    geo_details = responsee.json()  
    record = []  
    count = 0      
    for item in geo_details: 
        for key in item.keys():             
             for segment in item[key]:
                data={}
                data['doc_date'] = datetime.strptime(key, '%Y-%m-%d')
                data['_index'] = 'tdap_financial_company_geography'
                data['symbol'] = company
                data['geo_name'] = segment
                data['value'] = item[key][segment]
                data['year'] = key.split('-')[0].strip()                
                data['_id'] = company + '_' + key + '_'+segment.lower().replace(' ','_')
                data['load_date'] = datetime.today()
                data['doc_type'] = "financial_company_geography"
                data['company_name'] = company_name
                data['exchange'] = exchange_name
                if flag == 'I' and count >=4:
                    break
                record.append(data)
    if len(record) > 0:
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing finacial segments for company :{company}')
        # print(f'number of records inserted :{res}')
        insert_records('Financial_Revenue_Segmentation', record)

def get_company_yearly_financial_ratio(company, company_name, exchange_name):
    print(f'processing finacial segments for company :{company}')
    # api_key = ''
    #annual    
    url = f'https://financialmodelingprep.com/api/v3/ratios/{company}?limit=2&apikey={api_key}' #limit=40 (hostorical)
    response = requests.get(url)
    record = []
    for item in response.json():
        data = {}
        data = item.copy()
        data['_id'] = data['symbol'] + '_' + data['date']
        data['doc_date'] = data['date']
        data['load_date'] = datetime.today()
        data['calenderYear'] = int(data['date'].split('-')[0].strip())
        data['_index'] = 'tdap_financial_ratio_yearly'
        data['doc_type'] = 'finance_ratio_yearly'
        data['company_name'] = company_name
        data['exchange'] = exchange_name
        record.append(data)
    if len(record) > 0:
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing finacial segments for company :{company}')
        # print(f'number of records inserted :{res}')
        insert_records('Financial_Annual_Ratios', record)


def get_company_quarterly_financial_ratio(company, company_name, exchange_name):
    print(f'processing finacial ratios for company :{company}')
    # api_key = ''
    #annual    
    url = f'https://financialmodelingprep.com/api/v3/ratios/{company}?period=quarter&limit=4&apikey={api_key}' #limit=400(historical)
    response = requests.get(url)
    record = []
    for item in response.json():
        data = {}
        data = item.copy()
        data['_id'] = data['symbol'] + '_' + data['date']
        data['doc_date'] = data['date']
        data['load_date'] = datetime.today()
        data['calenderYear'] = int(data['date'].split('-')[0].strip())
        data['year_quarter'] = str(data['calenderYear']) + '.' + data['period']
        data['_index'] = 'tdap_financial_ratio_quarterly'
        data['doc_type'] = 'finance_ratio_quarter'
        data['company_name'] = company_name
        data['exchange'] = exchange_name
        record.append(data)
    if len(record) > 0:
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing finacial ratios for company :{company}')
        # print(f'number of records inserted :{res}')   
        insert_records('Financial_Quaterly_Ratios', record) 

def get_stock_financial_scores(company, company_name, exchange_name):
    print(f'processing finacial scores for company :{company}')
    # api_key = ''
    #annual    
    url = f'https://financialmodelingprep.com/api/v4/score?symbol={company}&apikey={api_key}'

    response = requests.get(url)
    record = []
    for item in response.json():
        # print(item)
        # exit()
        data = {}
        
        data['_id'] = item['symbol'] + datetime.strftime(datetime.today(), "%Y_%m_%d")
        data['altmanZScore'] = item['altmanZScore']
        data['piotroskiScore'] = item['piotroskiScore']
        if item['workingCapital']:
            if 'E' in str(item['workingCapital']):
                value,power = item['workingCapital'].split('E')
                data['workingCapital'] = float(value) * (10 ** int(power))
            else:
                data['workingCapital'] = item['workingCapital']
        if item['totalAssets']:       
            if 'E' in str(item['totalAssets']):
                value,power = item['totalAssets'].split('E')
                data['totalAssets'] = float(value) * (10 ** int(power))
            else:
                data['totalAssets'] = item['totalAssets']

        if item['retainedEarnings'] :      
            if 'E' in str(item['retainedEarnings']):
                value,power = item['retainedEarnings'].split('E')
                data['retainedEarnings'] = float(value) * (10 ** int(power))
            else:
                data['retainedEarnings'] = item['retainedEarnings']

        if item['ebit']:        
            if 'E' in str(item['ebit']):
                value,power = item['ebit'].split('E')
                data['ebit'] = float(value) * (10 ** int(power))
            else:
                data['ebit'] = item['ebit']    
        if  item['marketCap']:      
            if 'E' in str(item['marketCap']):
                value,power = item['marketCap'].split('E')
                data['marketCap'] = float(value) * (10 ** int(power))
            else:
                data['marketCap'] = item['marketCap'] 

        if  item['totalLiabilities']:            
            if 'E' in str(item['totalLiabilities']):
                value,power = item['totalLiabilities'].split('E')
                data['totalLiabilities'] = float(value) * (10 ** int(power))
            else:
                data['totalLiabilities'] = item['totalLiabilities']  

        if item['revenue']:  
            if 'E' in str(item['revenue']):
                value,power = item['revenue'].split('E')
                data['revenue'] = float(value) * (10 ** int(power))
            else:
                data['revenue'] = item['revenue']   

        data['doc_date'] = datetime.today()
        data['load_date'] = datetime.today()
        data['Year'] = datetime.now().year       
        data['_index'] = 'tdap_financial_score'
        data['doc_type'] = 'finance_score'
        data['company_name'] = company_name
        data['exchange'] = exchange_name
        data['symbol'] = item['symbol'] 
        record.append(data)
    if len(record) > 0:
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing finacial scores for company :{company}')
        # print(f'number of records inserted :{res}') 
        insert_records('Financial_Scores', record)

def get_company_enterprise_value(company, company_name, exchange_name):
    print(f'processing enterprise value for company :{company}')
    # api_key = ''
    #annual    
    url = f'https://financialmodelingprep.com/api/v3/enterprise-values/{company}?period=quarter&limit=10&apikey={api_key}' #limit=130 (historical)
    response = requests.get(url)
    record = []
    for item in response.json():
        data = {} 
        data = item.copy()       
        data['_id'] = item['symbol'] + '_' + item['date']
        data['doc_date'] = item['date']
        data['load_date'] = datetime.today()
        data['calenderYear'] = int(data['date'].split('-')[0].strip())         
        data['_index'] = 'tdap_financial_enterprise_value'
        data['doc_type'] = 'finance_enterprise_value'
        data['company_name'] = company_name
        data['exchange'] = exchange_name
        record.append(data)
    if len(record) > 0:
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing finacial ratios for company :{company}')
        # print(f'number of records inserted :{res}')   
        insert_records('Financial_Enterprise_Value', record)                   

def get_stock_ownership_data(company, company_name, exchange_name,start_year, end_year):    
    print(f'processing stock ownership  for company :{company}')
    # api_key = ''
    record = []       
    for year in range(start_year,end_year):
        next = True
        page_no = 0
        while next:
            url = f'https://financialmodelingprep.com/api/v4/institutional-ownership/institutional-holders/symbol-ownership-percent?date={year}-09-30&symbol={company}&page={page_no}&apikey={api_key}'
            print(url)
            response = requests.get(url)
            print('No Of records returned : {}'.format(len(response.json())))
            if len(response.json()) < 50: #per page data count max 50
                next = False
            else:
                page_no += 1
            
            for item in response.json():
                data = {} 
                data = item.copy()       
                data['_id'] = company + '_' + item['cik'] + '_' + item['filingDate'] #cik is the cik of the institution 
                data['doc_date'] = item['filingDate']
                data['load_date'] = datetime.today()                
                data['_index'] = 'tdap_financial_stock_ownership'
                data['doc_type'] = 'finance_stock_ownership'
                data['company_name'] = company_name
                data['exchange'] = exchange_name
                if abs(data['changeInMarketValue']) < 2 ** 62 and abs(data['marketValue']) < 2 ** 62 :
                    record.append(data)
    if len(record) > 0:
        insert_records('Financial_Stock_Ownership', record)
        # print(record)
        # # res=helpers.bulk(es_client,record)
        # print(f'Finished processing stock ownership for company :{company}')
        # # print(f'number of records inserted :{res}')  

def get_company_ESG_value(company, company_name, exchange_name):
    print(f'processing ESG score for company :{company}')
    # api_key = ''  
    url = f'https://financialmodelingprep.com/api/v4/esg-environmental-social-governance-data?symbol={company}&apikey={api_key}'
    response = requests.get(url)
    record = []
    for item in response.json():
        data = {}          
        if item['symbol'] == 'FB':
            data['symbol'] = 'META'
        else:    
            data['symbol'] =  item['symbol']
        data['cik'] =  item['cik']
        data['company_name'] =  item['companyName']
        data['formType'] =  item['formType']
        data['acceptedDate'] =  item['acceptedDate']
        data['date'] =  item['date']
        data['environmentalScore'] =  item['environmentalScore']
        data['socialScore'] =  item['socialScore']
        data['governanceScore'] =  item['governanceScore']
        data['ESGScore'] =  item['ESGScore']
        data['url'] =  item['url'] 
        data['_id'] = data['symbol'] + '_' + item['date']
        data['doc_date'] = item['date']
        data['load_date'] = datetime.today()            
        data['_index'] = 'tdap_financial_esg'
        data['doc_type'] = 'finance_esg_score'      
        data['exchange'] = exchange_name
        record.append(data)
    if len(record) > 0:
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing ESG score for company :{company}')
        # print(f'number of records inserted :{res}')
        insert_records('Financial_ESG_Score', record) 

def get_industrial_classification():
    print(f'processing industrial classification')
    # api_key = ''        
    url = f'https://financialmodelingprep.com/api/v4/standard_industrial_classification/all?apikey={api_key}'
    response = requests.get(url)
    record = []
    for item in response.json():
        data = {} 
        data['cik'] =  item['cik']
        data['company_name'] =  item['name']
        data['sicCode'] =  item['sicCode']
        data['industryTitle'] =  item['industryTitle']       
        data['businessAdress'] =  item['businessAdress']
        data['phoneNumber'] =  item['phoneNumber']     
        data['symbol'] = item['symbol']
        data['_id'] = item['symbol'] + '_' + item['cik']
        data['doc_date'] = datetime.today() 
        data['load_date'] = datetime.today()            
        data['_index'] = 'tdap_financial_industrial_classification'
        data['doc_type'] = 'finance_ic' 
               
        record.append(data)

    if len(record) > 0:
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing industrial classification')
        # print(f'number of records inserted :{res}') 
        insert_records('Financial_Industrial_Classification', record)    

def get_earning_surprises_data(company, company_name, exchange_name):
    print(f'processing earning suprises for company :{company}')
    # api_key = ''        
    url = f'https://financialmodelingprep.com/api/v3/earnings-surprises/{company}?apikey={api_key}&limit=4'
    response = requests.get(url)
    record = []
    for item in response.json():
        data = {}      
        if item['symbol'] == 'FB':
            data['symbol'] = 'META'
        else:    
            data['symbol'] =  item['symbol'] 
        
        data['company_name'] =  company_name
        data['doc_date'] =  item['date']
        data['actualEarningResult'] =  item['actualEarningResult']  
        if item['estimatedEarning']:
            data['estimatedEarning'] =  item['estimatedEarning']              
            if item['actualEarningResult'] > item['estimatedEarning']:
                data['status']  = 'beat'
            if item['actualEarningResult'] < item['estimatedEarning']:
                data['status']  = 'miss'    
            if item['actualEarningResult'] ==item['estimatedEarning']:
                data['status']  = 'met'    

        data['_id'] = data['symbol'] + '_' + item['date']        
        data['load_date'] = datetime.today()            
        data['_index'] = 'tdap_financial_er_surprise'
        data['doc_type'] = 'finance_es'      
        data['exchange'] = exchange_name     
        record.append(data)        
    if len(record) > 0:
        # # res=helpers.bulk(es_client,record)
        # print(record)
        # print(f'Finished processing earning suprises for company :{company}')
        # # print(f'number of records inserted :{res}') 
        insert_records('Financial_Earning_Suprises', record)  

def get_analyst_estimates_data(company, company_name, exchange_name):
    print(f'processing analyst estimates for company :{company}')
    # api_key = ''        
    url = f'https://financialmodelingprep.com/api/v3/analyst-estimates/{company}?period=quarter&limit=10&apikey={api_key}'
    response = requests.get(url)
    record = []
    for item in response.json():
        data = {}      
        if item['symbol'] == 'FB':
            data['symbol'] = 'META'
        else:    
            data['symbol'] =  item['symbol'] 
        
        data['company_name'] =  company_name
        data['doc_date'] =  item['date']      
        data['_id'] = data['symbol'] + '_' + item['date']        
        data['load_date'] = datetime.today()            
        data['_index'] = 'tdap_financial_analyst_est'
        data['doc_type'] = 'finance_analyst_est'      
        data['exchange'] = exchange_name   
        data['estimatedRevenueLow'] =  item['estimatedRevenueLow'] 
        data['estimatedRevenueHigh'] =  item['estimatedRevenueHigh']   
        data['estimatedRevenueAvg'] =  item['estimatedRevenueAvg'] 
        data['estimatedEbitdaLow'] =  item['estimatedEbitdaLow'] 
        data['estimatedEbitdaHigh'] =  item['estimatedEbitdaHigh'] 
        data['estimatedEbitdaAvg'] =  item['estimatedEbitdaAvg'] 
        data['estimatedEbitLow'] =  item['estimatedEbitLow'] 
        data['estimatedEbitHigh'] =  item['estimatedEbitHigh'] 
        data['estimatedEbitAvg'] =  item['estimatedEbitAvg'] 
        data['estimatedNetIncomeLow'] =  item['estimatedNetIncomeLow'] 
        data['estimatedNetIncomeHigh'] =  item['estimatedNetIncomeHigh'] 
        data['estimatedNetIncomeAvg'] =  item['estimatedNetIncomeAvg'] 
        data['estimatedSgaExpenseLow'] =  item['estimatedSgaExpenseLow'] 
        data['estimatedSgaExpenseHigh'] =  item['estimatedSgaExpenseHigh'] 
        data['estimatedSgaExpenseAvg'] =  item['estimatedSgaExpenseAvg']
        data['estimatedEpsAvg'] =  item['estimatedEpsAvg']
        data['estimatedEpsHigh'] =  item['estimatedEpsHigh']
        data['estimatedEpsLow'] =  item['estimatedEpsLow']
        data['numberAnalystEstimatedRevenue'] =  item['numberAnalystEstimatedRevenue']
        data['numberAnalystsEstimatedEps'] =  item['numberAnalystsEstimatedEps']
        record.append(data)        
    if len(record) > 0:
        insert_records('Financial_Analyst_Estimates', record)
        # print(record)
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing analyst estimates  for company :{company}')
        # print(f'number of records inserted :{res}')       

def get_merger_acquisition_data():
    print(f'processing merger acquisition data')
    # api_key = ''       
    page_count = 0
    next =True 
    record = []
    load_type = 'incremental'
    while next:
        url = f'https://financialmodelingprep.com/api/v4/mergers-acquisitions-rss-feed?page={page_count}&apikey={api_key}'
        if load_type == 'incremental': # for incremental load get data from latest page every month
            next = False
        response = requests.get(url)        
        if len(response.json()) == 100:
            page_count += 1
        else:
            next = False    
        for item in response.json():
            data = {}               
            data['doc_date'] =  datetime.strptime(item['acceptanceTime'] , '%Y-%m-%d %H:%M:%S')   
            data['_id'] = item['acceptanceTime'].replace(' ','_').replace(':','_').replace('-','_')     
            data['load_date'] = datetime.today()            
            data['_index'] = 'tdap_financial_merger_acquisition'
            data['doc_type'] = 'finance_merger_acquisition'      
            
            data['companyName'] =  item['companyName']  
            data['cik'] =  item['cik'] 
            data['symbol'] =  item['symbol'] 
            data['targetedCompanyName'] =  item['targetedCompanyName']
            data['targetedCik'] =  item['targetedCik'] 
            data['targetedSymbol'] =  item['targetedSymbol']             
            data['transactionDate'] =  item['transactionDate'] 
            data['acceptanceTime'] =  item['acceptanceTime'] 
            data['url'] =  item['url'] 
      
            record.append(data)        
    if len(record) > 0:
        insert_records('Financial_Merger_Acquisition', record)
        # res=helpers.bulk(es_client,record)
        # print(f'Finished processing merger acquisition data')
        # print(f'number of records inserted :{res}') 


   

def get_economic_indicator_data():
    print(f'processing finacial indicator data')
    # api_key = ''   
    start_year = datetime.now().year - 1
    end_year = datetime.now().year
    economic_indicators = 'GDP | realGDP | nominalPotentialGDP | realGDPPerCapita | federalFunds | CPI | inflationRate | inflation | retailSales | consumerSentiment | durableGoods | unemploymentRate | totalNonfarmPayroll | initialClaims | industrialProductionTotalIndex | newPrivatelyOwnedHousingUnitsStartedTotalUnits | totalVehicleSales | retailMoneyFunds | smoothedUSRecessionProbabilities | 3MonthOr90DayRatesAndYieldsCertificatesOfDeposit | commercialBankInterestRateOnCreditCardPlansAllAccounts | 30YearFixedRateMortgageAverage | 15YearFixedRateMortgageAverage'
    for indicator in economic_indicators.split('|'):
        indicator = indicator.strip()
        gdp_url = 'https://financialmodelingprep.com/api/v4/economic?name={}&from={}-01-01&to={}-01-01&apikey={}'.format(indicator, start_year, end_year, api_key)
        gdp_response = requests.get(gdp_url)
        record = []
        for item in  gdp_response.json():
            data = {}
            data['date'] = item['date']
            data['indicator'] = indicator
            data['value'] = item['value']
            data['_index'] = 'tdap_financial_economic_indicator'
            data['_id'] =  indicator + '_' + data['date'] 
            data['load_date'] = datetime.today()     
            data['doc_date'] = item['date']
            data['doc_type'] = "financial_economic_indicator"
            record.append(data)
    
   
        if len(record) > 0:
            # res=helpers.bulk(es_client,record)
            # print(f'number of records inserted for indicator {indicator} is :{res}')
            insert_records('Financial_Indicators', record)
        print(f'Finished processing finacial indicator : {indicator}')

if datetime.today().day == 21:
    if datetime.today().month in [2,4,6,8]: 
        get_economic_indicator_data()
        get_merger_acquisition_data()
    if datetime.today().month == 6: 
        get_industrial_classification()

try:
    start_year, end_year = datetime.now().year - 1, datetime.now().year
    exchange_name_list = ['NASDAQ', 'NYSE', 'AMEX']

    for exchange_name in exchange_name_list:
        tickers = get_tickers(exchange_name)
        for index, row in tickers.iterrows():
            company = row['symbol']
            company_name = row['name']
            #20
            if datetime.today().day == 14 and datetime.today().month in [2, 4, 7, 11,12]:
                logging.info(f'Processing - {index} company - {company_name} exchange - {exchange_name}')
                get_financial_10k_data(company, company_name, exchange_name)

            if datetime.today().day == 21 and datetime.today().month in [2,4,7,12] :    
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')
                get_financial_10q_data(company, company_name, exchange_name)
            # 22
            if datetime.today().day == 22 and datetime.today().month in [2,4,7,12]:
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')
                get_earning_transcript_historical(company, company_name, exchange_name, start_year, end_year)  
            
            if datetime.today().day == 23 and datetime.today().month in [2,4,7,12]:   
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}') 
                get_analyst_estimates_data(company, company_name, exchange_name)

            if datetime.today().day == 24 and datetime.today().month in [2,4,7,12]:     
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')
                get_earning_surprises_data(company, company_name, exchange_name)      

            if datetime.today().day == 25 and datetime.today().month in [2,4,7,12]: 
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')
                get_stock_ownership_data(company, company_name, exchange_name, start_year, end_year)
            
            if datetime.today().day == 26 and datetime.today().month in [2,4,7,12]: 
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')
                get_company_enterprise_value(company, company_name, exchange_name)
            #27
            if datetime.today().day == 27 and datetime.today().month in [2,4,7,12]:  
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')   
                get_stock_financial_scores(company, company_name, exchange_name)

            if datetime.today().day == 28 and datetime.today().month in [2,4,7,12]: 
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')    
                get_company_quarterly_financial_ratio(company, company_name, exchange_name)

            if datetime.today().day == 29 and datetime.today().month in [12]: 
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')    
                get_company_yearly_financial_ratio(company, company_name, exchange_name) 
            
            if datetime.today().day == 15 and datetime.today().month in [2,4,7,12]:
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')
                get_company_finacial_by_segment(company, company_name, exchange_name)
            
            if datetime.today().day == 16 and datetime.today().month in [2,4,7,12]: 
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')
                get_company_finacial_by_geographies(company, company_name, exchange_name)        
            
            if datetime.today().day == 17 and datetime.today().month in [4,8,12]:
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')
                get_company_ESG_value(company, company_name, exchange_name)
            
            if datetime.today().day == 18 and datetime.today().month in [6,12]:
                print(f'Processing - {index} comapny - {company_name} exchange - {exchange_name}')
                get_company_profile_data(company)

except KeyboardInterrupt:
    error_message = "Process interrupted by user."
    logging.error(error_message)
    log_update("N/A", "N/A", current_collection, 'FMP_LogCollection', error_message)

except Exception as e:
    error_message = f"An unexpected error occurred: {str(e)}\n{traceback.format_exc()}"
    logging.error(error_message)
    log_update("N/A", "N/A", current_collection, 'FMP_LogCollection', error_message)