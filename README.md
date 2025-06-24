# Earnings-calls-search-engine

An interactive Python Dash web application that enables market research analysts to extract contextual insights from earnings call transcripts with ease and precision.
The system supports keyword-based, context-rich search over parsed transcripts, powered by a custom MongoDB backend and FMP APIs for financial data integration. It is tailored for competitive intelligence and investor relations workflows.

🔍 Key Features:
🔍 Automatic Synonym Expansion  – 
Each user keyword is matched against a curated synonym bank stored in MongoDB, enabling broader and more intelligent search coverage.
🔍 Text Cleaning & Segmentation  – 
Transcripts are preprocessed to distinguish between Prepared Remarks and Q&A sections, ensuring high relevance in search results.
Speaker Attribution: Each sentence is structured and tagged with the correct speaker name, enabling role-specific insights (e.g., CEO vs Analyst responses).
🔍 Contextual Search Results  – 
Outputs are not just matches, but full-context segments that help users understand the meaning behind the mention.
🔍 Backend Storage  – 
All transcripts and metadata are stored and indexed within MongoDB for fast, flexible querying.

🛠 Built With:
🛠 Python Dash – for frontend interactivity
🛠 MongoDB – for scalable, indexed storage and advanced querying
🛠 FMP APIs – for integrating financial metadata
🛠 NLP tools – for text parsing, segmentation, and speaker tagging

📽️ Demo
Check out the live walkthrough of the application in action:

https://github.com/user-attachments/assets/41426f46-2ccb-4ec9-b696-af5a844fcd29

🚀 Setup Instructions  
  🛠️ 1. Clone the Repository  
        git clone repository-url  
        cd repository-folder  
  🌱 2. Create a Virtual Environment (Optional)  
          python -m venv venv  
          🔒 Activate the Virtual Environment:  
              On Linux/Mac:  
              source venv/bin/activate  
              On Windows:  
              venv\Scripts\activate  
    📦 3. Install Dependencies  
          pip install -r requirements.txt  
    ▶️ 4. Run the Project  
          python <your_script_name>.py  

🔌 Data Source
This project uses the Financial Modeling Prep API for accessing real-time and historical earnings call data:
https://site.financialmodelingprep.com/


🖥️ Console View
Here’s a glimpse of the backend console showing real-time parsing and search execution:
![image](https://github.com/user-attachments/assets/48049189-4e41-4cad-8a10-eabb59920341)


🗃️ MongoDB Backend
The system relies heavily on MongoDB for:
🗃️ Storing cleaned and structured transcripts
🗃️ Segmenting text into Prepared Remarks and Q&A
🗃️ Expanding search queries using a synonym bank
🗃️ Tagging sentences with correct speaker roles

📌 Example Snapshots:
![image](https://github.com/user-attachments/assets/d287645b-02be-4ace-a46f-dc9b76c43db4)
![image](https://github.com/user-attachments/assets/dce74e43-63e8-49b6-8ae1-2ef688f0c4aa)
![image](https://github.com/user-attachments/assets/5b73d1d4-d758-481c-ad6a-ed6e81a9aa04)

