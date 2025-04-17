import pandas as pd
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load resume summary data
conn = sqlite3.connect(r"D:\Hackathon\Dataset\smarthire.db")
df_resume = pd.read_sql_query("SELECT * FROM resume_summary2", conn)

# Initialize lists for embeddings
role_embeddings, experience_embeddings, skills_embeddings = [], [], []

# Loop over records and compute embeddings
for _, row in df_resume.iterrows():
    # Safeguard against missing/null fields
    role = row['role'] if pd.notna(row['role']) else ''
    experience = row['experience'] if pd.notna(row['experience']) else ''
    skills = row['skills'] if pd.notna(row['skills']) else ''

    # Generate and convert to byte format for SQLite storage
    role_embeddings.append(model.encode(role).astype(np.float32).tobytes())
    experience_embeddings.append(model.encode(experience).astype(np.float32).tobytes())
    skills_embeddings.append(model.encode(skills).astype(np.float32).tobytes())

# Add to DataFrame
df_resume['role_embeddings'] = role_embeddings
df_resume['experience_embeddings'] = experience_embeddings
df_resume['skills_embeddings'] = skills_embeddings



# Assuming `df_resume` is your DataFrame containing the byte-encoded embeddings
df_resume['role_vector'] = df_resume['role_embeddings'].apply(lambda x: np.frombuffer(x, dtype=np.float32))
df_resume['experience_vector'] = df_resume['experience_embeddings'].apply(lambda x: np.frombuffer(x, dtype=np.float32))
df_resume['skills_vector'] = df_resume['skills_embeddings'].apply(lambda x: np.frombuffer(x, dtype=np.float32))


# Save as new table (or replace)
df_resume.to_sql("resume_embeddings", conn, if_exists="replace", index=False)
#conn.close()

print(df_resume['experience_vector'])
print(df_resume['skills_vector'])
print(df_resume['role_vector'])


print("✅ Resume embeddings saved to 'resume_embeddings' table.")
