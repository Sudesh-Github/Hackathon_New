import os
import sqlite3
import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub

import os
from PyPDF2 import PdfReader
import sqlite3
import pandas as pd

# Folder with resumes
folder_path = r"D:\Hackathon\Dataset\[Usecase 5] AI-Powered Job Application Screening System\CVs1"

# Get first 2 PDF files only
pdf_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')])[:2]

# Open DB connection
conn = sqlite3.connect(r"D:\Hackathon\Dataset\smarthire.db")

# Loop over only first 2 resumes
for filename in pdf_files:
    file_path = os.path.join(folder_path, filename)
    reader = PdfReader(file_path)
    text = "\n".join([page.extract_text() or "" for page in reader.pages])

    # Save into DataFrame (1 row)
    df = pd.DataFrame([{
        "file_name": filename,
        "resume_text": text
    }])

    # Save to DB
    df.to_sql("resume", conn, if_exists="append", index=False)

conn.close()
print("✅ First 2 resumes saved to SQLite!")



# ------------------- CONFIG -------------------
HUGGINGFACEHUB_API_TOKEN = ""  # Replace with your Hugging Face token
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

DB_PATH = r"D:\Hackathon\Dataset\smarthire.db"

# ------------------- PROMPT TEMPLATE -------------------
resume_prompt = PromptTemplate.from_template("""You are a helpful assistant that extracts structured information from resumes.

Extract the following fields:
1. Role - (Job Title or most likely role)
2. Gmail ID - (Only Gmail email address)
3. Work Experience - (Company names, dates, and short achievements)
4. Skills - (Key technical and soft skills)

Respond ONLY in this format:

Role - <role>

Gmail ID - <gmail>

Work Experience - 
<work_experience text>

Skills - 
<skills text>

Resume:
{text}
""")

# ------------------- LLM SETUP -------------------
llm = HuggingFaceHub(
    repo_id="google/flan-t5-large",  # or try 'mistralai/Mistral-7B-Instruct-v0.1'
    model_kwargs={"temperature": 0.3, "max_new_tokens": 200}
)

pipeline = resume_prompt | llm

# ------------------- READ RESUMES -------------------
conn = sqlite3.connect(DB_PATH)
resumes = pd.read_sql_query("SELECT file_name, resume_text FROM resume", conn)

# ------------------- FIELD EXTRACTION -------------------



results = []
for _, row in resumes.iterrows():
    try:
        response = pipeline.invoke({"text": row["resume_text"]})
        response_text = response if isinstance(response, str) else response.content

        print(f"\n🔍 Extracted from {row['file_name']}\n{response_text}\n")

        fields = {"file_name": row["file_name"]}
        

        # Parsing the response to extract the relevant fields
        role = None
        gmail = None
        work_experience = None
        skills = None
        
        # Split the response into lines and process
        for line in response_text.split("\n"):
            line = line.strip()
            if line.startswith("Role - "):
                role = line.split("Role - ")[1].strip()
            elif line.startswith("Gmail ID - "):
                gmail = line.split("Gmail ID - ")[1].strip()
            elif line.startswith("Work Experience - "):
                experience_start = response_text.split("Work Experience - ")[1]
                experience_end = experience_start.split("Skills -")[0]
                experience = experience_end.strip()
            elif line.startswith("Skills - "):
                skills_start = response_text.split("Skills - ")[1]
                skills = skills_start.strip()
                break

        # Add fields to the results if they are extracted
        if role or gmail or work_experience or skills:
            fields.update({"role": role, "gmail": gmail, "experience": work_experience, "skills": skills})
            results.append(fields)
        else:
            print(f"⚠️ No structured data extracted from {row['file_name']}")

    except Exception as e:
        print(f"❌ Error extracting fields from {row['file_name']}: {e}")
        
#print("✅ Extracted Fields:")
#for k, v in fields.items():
#    print(f"{k}: {repr(v)}")  # Use repr() to clearly see special characters or newlines


# ------------------- SAVE TO SQLITE -------------------
if results:
    df_structured = pd.DataFrame(results)
    df_structured.to_sql("resume_summary", conn, if_exists="replace", index=False)
    print("✅ Resume data successfully saved to 'resume_summary'")
else:
    print("⚠️ No data was extracted.")

