

# !pip install langchain-google-genai
# !pip install langchain-groq
# !pip install PyPDF2

import pandas as pd
import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
from PyPDF2 import PdfReader
import os

"""### **Read**"""

data = pd.DataFrame(columns=None)
data['name'], data['gmail'], data['phone'], data['role'] , data['work_experince'], data['skills'], data['relevance'] = '', '', '','','', '', ''

data['role_embeddings'],data['work_experience_embeddings'],data['skills_embeddings'] ,data['relevance_embeddings'] ='', '','',''
print(data)

sections_to_extract = ["name", "gmail", "current role", "work experience", "skills"]

name_list, gmail_list, phone_list, role_list, work_experience_list, skills_list, relevance_list  = [], [], [], [], [], [], []
role_embeddings_list, work_experience_embeddings_list, skills_embeddings_list, relevance_embeddings_list = [], [], [], []

pdf_files = [f for f in os.listdir(r"D:\Hackathon\Dataset\[Usecase 5] AI-Powered Job Application Screening System\CVs1") if f.lower().endswith('.pdf')]
pdf_files.sort()
for filename in pdf_files[:20]:
    file_path = os.path.join(r"D:\Hackathon\Dataset\[Usecase 5] AI-Powered Job Application Screening System\CVs1", filename)
    file = PdfReader(file_path)
    read = "\n".join([i.extract_text() for i in file.pages])
    relevance_list.append(read)

example_output = """
Example format:

Extract only the role name:
e.g., Software Engineer

Extract Name:
e.g., Scott Saunders

Extract Gmail:
e.g., scottsaunders13@gmail.com

Extract Phone:
e.g., +1-202-555-0172

Extract Work Experience:
Data Scientist at ABC Inc. (2019–2023)
Built predictive models that enhanced decision-making processes, reducing operational costs by 25%.

Extract Skills:
Cybersecurity – Skilled in penetration testing, risk assessment, and securing enterprise networks against cyber threats.
"""

"""### **Model**"""

api_key = " " # Insert API Key
llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-2.0-flash")
model = SentenceTransformer('all-MiniLM-L6-v2')

for resume in relevance_list:
    # Embed full resume
    relevance_embeddings_list.append(model.encode(resume).astype(np.float32).tobytes())

    for section in sections_to_extract:
        # Dynamic prompt for each section
        prompt = f"""
You are an AI assistant extracting structured information from resumes.

Extract only the **{section}** section from the following resume. Use the format shown in the example.

Resume:
\"\"\"{resume}\"\"\"

Example format:
{example_output}
"""

        # Get LLM response
        response = llm.invoke(prompt).content.strip()

        # Append to appropriate lists
        if section == "name":
            name_list.append(response)


        elif section == "gmail":
            gmail_list.append(response)
            
        elif section == "phone":
            phone_list.append(response)

        elif section == "current role":
            role_list.append(response)
            role_embeddings_list.append(model.encode(response).astype(np.float32).tobytes())

        elif section == "work experience":
            work_experience_list.append(response)
            work_experience_embeddings_list.append(model.encode(response).astype(np.float32).tobytes())

        elif section == "skills":
            skills_list.append(response)
            skills_embeddings_list.append(model.encode(response).astype(np.float32).tobytes())

# print(f'role-{role_list}\n')
# print(f'role-{gmail_list}\n')
# print(f'role-{name_list}\n')
print(f'role-{phone_list}\n')
# print(f'role-{relevance_list}\n')
# print(f'role emb-{role_embeddings_list}\n')
# print(f'work experience-{work_experience_list}\n')
# print(f'work experience emb-{work_experience_embeddings_list}\n')
# print(f'skills-{skills_list}\n')
# print(f'skills emb-{skills_embeddings_list}\n')

# Define target query or job description (this can be dynamic too)
target_description = """
Role: Data Scientist
Experience: 3+ years in data analysis, machine learning, and predictive modeling.
Skills: Python, SQL, TensorFlow, Scikit-learn, Data Visualization, Big Data Tools
"""

# Encode the target/job description for each component
target_role = "Data Scientist"
target_experience = "3+ years in data analysis, machine learning, predictive modeling"
target_skills = "Python, SQL, TensorFlow, Scikit-learn, Data Visualization, Big Data Tools"
target_relevance = target_description  # or the full description

# Create target embeddings
target_role_emb = model.encode(target_role).reshape(1, -1)
target_experience_emb = model.encode(target_experience).reshape(1, -1)
target_skills_emb = model.encode(target_skills).reshape(1, -1)
target_relevance_emb = model.encode(target_relevance).reshape(1, -1)

# Similarity Threshold
threshold = 0.80

print("\n\n--- Matching Candidates ---\n")

# Iterate through all extracted embeddings
for i in range(len(name_list)):
    role_emb = np.frombuffer(role_embeddings_list[i], dtype=np.float32).reshape(1, -1)
    experience_emb = np.frombuffer(work_experience_embeddings_list[i], dtype=np.float32).reshape(1, -1)
    skills_emb = np.frombuffer(skills_embeddings_list[i], dtype=np.float32).reshape(1, -1)
    relevance_emb = np.frombuffer(relevance_embeddings_list[i], dtype=np.float32).reshape(1, -1)

    # Compute individual cosine similarities
    sim_role = cosine_similarity(role_emb, target_role_emb)[0][0]
    sim_experience = cosine_similarity(experience_emb, target_experience_emb)[0][0]
    sim_skills = cosine_similarity(skills_emb, target_skills_emb)[0][0]
    sim_relevance = cosine_similarity(relevance_emb, target_relevance_emb)[0][0]

    # Weighted score
    total_score = (
        0.2 * sim_role +
        0.35 * sim_experience +
        0.35 * sim_skills +
        0.1 * sim_relevance
    )

    # Print only if score > threshold
    if total_score >= threshold:
        print(f"Name: {name_list[i]}")
        print(f"Gmail: {gmail_list[i]}")
        print(f"Phone: {phone_list[i]}")
        print(f"Match Score: {total_score:.2f}\n")

print("total score", total_score)






