
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
> Open `db_connection.py` and add your actual connection string.
> ```python
> MONGODB_URI = "your_mongodb_connection_string"
> ```  
> **5. Run the Project**  
> ```bash
> python earnings_search_dash_app.py
> ```


&nbsp;

### 🔌 Data Source
This project uses the Financial Modeling Prep API for accessing real-time and historical earnings call data:  
https://site.financialmodelingprep.com/

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

