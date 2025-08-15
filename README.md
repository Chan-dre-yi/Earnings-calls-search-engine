
# Earnings-calls-search-engine

An interactive Python Dash web application that enables market research analysts to extract contextual insights from earnings call transcripts with ease and precision.
The system supports keyword-based, context-rich search over parsed transcripts, powered by a custom MongoDB backend and FMP APIs for financial data integration. It is tailored for competitive intelligence and investor relations workflows.

&nbsp;

### 🔍 Key Features
- 🔍 **Automatic Synonym Expansion** – Each keyword is matched against a curated synonym bank, enabling more intelligent search coverage.
- 🔍 **Text Cleaning & Segmentation** – Transcripts are preprocessed to distinguish between Prepared Remarks and Q&A sections, ensuring high relevance in search results.
- 🔍 **Speaker Attribution** – Each sentence is structured and tagged with the correct speaker name, enabling role-specific insights (e.g., CEO vs Analyst responses).
- 🔍 **Contextual Search Results** – Outputs are not just matches, but full-context segments that help users understand the meaning behind the mention.
- 🔍 **Backend Storage** – All transcripts and metadata are stored and indexed within MongoDB for fast, flexible querying.

&nbsp;

### 🛠 Built With
- 🛠 **Python Dash** – for frontend interactivity
- 🛠 **MongoDB** – for scalable, indexed storage and advanced querying
- 🛠 **FMP APIs** – for integrating financial metadata
- 🛠 **NLP tools** – for text parsing, segmentation, and speaker tagging

&nbsp;

### 📽️ Demo
Check out the live walkthrough of the application in action:

https://github.com/user-attachments/assets/41426f46-2ccb-4ec9-b696-af5a844fcd29

&nbsp;

> ### 🚀 Setup Instructions  
> **1. Clone the Repository**  
> ```bash
> git clone https://github.com/Chan-dre-yi/Earnings-calls-search-engine
> cd Earnings-calls-search-engine
> ```  
> **2. Create a Virtual Environment**  
> ```bash
> python -m venv venv
> ```  
> **Activate it (Linux/Mac):**  
> ```bash
> source venv/bin/activate
> ```  
> **Activate it (Windows):**  
> ```bash
> venv\Scripts\activate
> ```  
> **3. Install Dependencies**  
> ```bash
> pip install -r requirements.txt
> ```  
> **4. Configure the Database URI**
> - Host a MongoDB instance (locally or via MongoDB Atlas).  
> - Open `db_connection.py` and add your actual connection string.
> ```python
> MONGODB_URI = "your_mongodb_connection_string"
> ```  
> **5. Get Your API Key**  
> - Visit [Financial Modeling Prep](https://site.financialmodelingprep.com/) and obtain an API key.  
> - Add your key to the relevant part of the  `test_db_script.py` script.
> ```python
> api_key = '' #your api key
> ```
> **6. Add Proxy Variables (if required)**  
> If you're behind a firewall or using restricted internet, set your proxy variables in the  `test_db_script.py` script like so:
> ```python
> os.environ["HTTP_PROXY"] = "http://your_proxy:port"
> os.environ["HTTPS_PROXY"] = "http://your_proxy:port"
> ```
> **7. Prepare the Database**  
> Run the 4 scripts inside the `DatabaseScripts/` folder (modify the collection names if/ as required)  
> ```bash
> cd DatabaseScripts
> python test_db_script.py
> python doc_text_segmentation_script.py
> python test_to_prod_script.py
> python synonyms_generation.py
> cd ..
> ```
> **8. Run the Project**  
> ```bash
> python earnings_search_dash_app.py
> ```


&nbsp;

### 🔌 Data Source
This project uses the Financial Modeling Prep API for accessing real-time and historical earnings call data:  
[Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs/)

&nbsp;

### 🖥️ Console View
Here’s a glimpse of the backend console showing real-time parsing and search execution: 
<img src="https://github.com/user-attachments/assets/48049189-4e41-4cad-8a10-eabb59920341" alt="Console View" width="600"/>

&nbsp;

### 🗃️ MongoDB Backend
The system relies heavily on MongoDB for:
- 🗃️ Storing cleaned and structured transcripts
- 🗃️ Segmenting text into Prepared Remarks and Q&A
- 🗃️ Expanding search queries using a synonym bank
- 🗃️ Tagging sentences with correct speaker roles

&nbsp;

### 📌 Example Snapshots
<img src="https://github.com/user-attachments/assets/d287645b-02be-4ace-a46f-dc9b76c43db4" alt="Example 1" width="600"/>

<img src="https://github.com/user-attachments/assets/dce74e43-63e8-49b6-8ae1-2ef688f0c4aa" alt="Example 2" width="600"/>

<img src="https://github.com/user-attachments/assets/5b73d1d4-d758-481c-ad6a-ed6e81a9aa04" alt="Example 3" width="600"/>

&nbsp;

### ❓ FAQ

#### ❓ What problem does this solve?  
- *"Market research analysts often rely on **secondary reports (e.g., Statista, consulting PDFs, investor decks)**. These rarely provide **direct quotes** or **speaker context** from earnings calls. Analysts waste hours cross-checking, verifying, and building PPTs.*  
*This tool makes it **un-imaginably easier** by combining **trusted data sources** with **direct transcripts/quotes**, letting analysts get **ground truth in seconds**, not days."*


#### ❓ Why not just use SQL instead of MongoDB?  
- *"Earnings call transcripts are **long, unstructured text** — with speakers, timestamps, sentiment, and topic tags. Modeling this in SQL would mean **complex joins and performance bottlenecks**.*  
*MongoDB allows **document-based storage**, making it **natural to index and query by speaker, keyword, or section**, with **faster full-text search**. It’s a perfect fit for **unstructured but query-heavy data**."*


#### ❓ How is this different from existing sources like SeekingAlpha or Yahoo Finance?  
- *"Platforms like **SeekingAlpha, Motley Fool, Yahoo Finance** provide access to earnings calls — but mostly in **article format or delayed transcripts**, often behind **paywalls**.*  
*Our tool provides **direct, fast, and structured access**: you can search **who said what, where, and in which quarter** instantly. It’s designed **for analysts’ workflows**, not general investors."*


#### ❓ What impact does it bring for analysts?  
- *"Analysts building PPTs for decision-makers usually spend **days compiling trusted figures** and **quotable insights**. This tool enables: 
a. Instant quote retrieval from executives’ words, b. Cross-quarter comparisons without manual digging, c. Faster, more reliable reports with traceable sources.
Net impact: **higher trust, less grunt work, faster insights.**"*

#### ❓ How was this project validated?  
- *"The stack and performance choices were **constantly reviewed by ultra-senior mentors (25–30 yrs experience)**. The approach — MongoDB + NLP pipeline — was confirmed as the **right direction for scale and usability**.*  
*The only reason it wasn’t pushed to production: **team re-org + deprioritization due to layoffs**, not technical infeasibility."*




