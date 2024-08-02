import pandas as pd
import streamlit as st
from openai import OpenAI
import os

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="",
)

def chat_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def read_etl_mapping(file_path):
    return pd.read_excel(file_path)

def read_prompt_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def construct_prompt(etl_mapping_df, prompt_template):
    prompt = prompt_template + "\n\nETL Mapping Document:\n"
    for _, row in etl_mapping_df.iterrows():
        prompt += f"{row['Stage Table']} | {row['Source Column']} | {row['Target Table']} | {row['Target Column']} | {row['Transformation']}\n"
    return prompt

def generate_validation_sql(prompt_template, etl_mapping_content):
    prompt = prompt_template + "\n\n" + etl_mapping_content
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates SQL validation queries from ETL mapping documents."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Streamlit UI 
st.title("ETL Mapping to Validation SQL Converter")

st.write("Upload your ETL mapping Excel document below:")

uploaded_file = st.file_uploader("Choose a file", type="xlsx")

if uploaded_file is not None:
    etl_mapping_df = read_etl_mapping(uploaded_file)
    prompt_template_path = os.path.join(os.path.dirname(__file__), 'prompt_template.txt')
    prompt_template = read_prompt_template(prompt_template_path)
    
    st.write("ETL Mapping Document:")
    st.dataframe(etl_mapping_df)

if st.button("Generate Validation SQL"):
    with st.spinner("Generating SQL..."):
        prompt_template_path = os.path.join(os.path.dirname(__file__), 'prompt_template.txt')
        prompt_template = read_prompt_template(prompt_template_path)
        etl_mapping_content = construct_prompt(etl_mapping_df, "")
        validation_sql = generate_validation_sql(prompt_template, etl_mapping_content)
        st.subheader("Generated Validation SQL")
        st.code(validation_sql, language="sql")
