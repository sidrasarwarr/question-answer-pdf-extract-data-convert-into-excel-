import streamlit as st
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import pandas as pd
import os
import re
from langchain.llms import OpenAI

# ... [rest of your imports]

# Set OpenAI API key
from constants import openai_key
os.environ["OPENAI_API_KEY"] = openai_key

# Function to process the PDF file and return the raw text
def process_pdf_file(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    raw_text = ''
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            raw_text += content
    return raw_text



def extract_quantities(text):
    # Define the regex pattern to match numbers, optionally with commas, and decimals
    
    regex_pattern = r'\b\d{1,3}(?:,\d{3})*\.?\d*\b'

    
    # Find all matches for the pattern
    matches = re.findall(regex_pattern, text, re.IGNORECASE)
    filtered_matches = [match[0] for match in matches if match[0] not in ['360','2021','2022','tonnes (tCO2-e)','tonnes (tCO 2-e)','t CO2-e','kgCO 2-e/sqm','tonnes (tCO 2-e)','year 1','Scope 2','Scope 1','Scope 3','t','Scope1','($m revenue/t.CO 2-e)', '30 June 2022',' 30 June 2021',' 30 June 2023']]

    # Convert the extracted numbers to floats, remove commas,
    # then convert them to strings to normalize the format
    standardized_matches = [str(int(float(match.replace(',', '')))) for match in matches]
    #filtered_matches = [match[0] for match in matches if match[0] not in ['360','2021','2022','tonnes (tCO2-e)','tonnes (tCO 2-e)','t CO2-e']]
    
    # Return the standardized matches as a single string separated by commas
    return ",".join(standardized_matches)
    
# Apply the function to the DataFrame
    df['Quantity'] = df['Answers'].apply(extract_quantities)
    #print(df)
#r'\b\d{1,3}(?:,\d{3})*t\b'


def extract_and_convert_to_float(s):
    # Regex pattern to extract the numeric part (ignoring the trailing 't')
    pattern = r'\b\d{1,3}(?:,\d{3})*\.?\d*\b'
    
    # Search for the pattern in the string
    match = re.search(pattern, s)
    
    if match:
        # Extract the numeric part
        numeric_part = match.group()
        
        # Remove commas for correct float conversion
        numeric_part = numeric_part.replace(',', '')

        try:
            # Convert to float
            return float(numeric_part)
        except ValueError:
            # Handle any conversion errors
            return "Error: Could not convert to float"
        else:
         return "No valid number found"

# Example usage
        example_string = "2,347t"
        extracted_float = extract_and_convert_to_float(example_string)
        extracted_float

    # Join the filtered matches into a single string
##def extract_quantities(text):
    # Define the regex pattern to match various numeric formats including
    # those with commas as thousands separators and decimals
    ##regex_pattern = r'(\b\d{1,3}(?:\d{9})*(?:\.\d+)?)(?!\s*(?:MWh|tonnes CO2-e|kl|cubic metres|Scope 2|Scope 1|t CO2-e|t CO 2-e))'


    df['Quantity'] = df['Answers'].apply(extract_quantities)

    # Combine the exclusion patterns into a single regex pattern
    exclusion_regex = '|'.join(exclusion_patterns)

    # Find potential quantities in the text
    potential_quantities = re.findall(r'([\d,]+\.?\d*)\s*(?:million|thousand|MT)?', text)

    # Filter out unwanted numbers
    quantities = [num for num in potential_quantities if not re.fullmatch(exclusion_regex, num.replace(',', ''))]

    # Return the cleaned quantities
    #return ",".join(quantities) if quantities else '-'
    #quantities = re.findall(r'([\d,]+\.?\d*)\s*(?:million|thousand|MT)?', text)
    return ",".join(quantities) if quantities else '-'

# Function to extract and standardize units from text
def extract_and_standardize_units(text):
    unit_patterns = {
    'million MWh': r'(?:32\.3\s+)?million megawatt hours',
    'KWh per m2': r'KWh per m2',
    'million m3': r'million cubic meters',
    'MT CO2e': r'metric ton CO2e',
    'MT CO2e': r'MT CO2e',
    '%': r'%',
    'm³': r'm³',
    'Employees': r'Employees',
    'Number': r'Number',
    'MWh': r'MWh',
    'MTCO2 e': r'MTCO2 e',
    '\(Metric Tons\)': r'\(Metric Tons\)',  # Escaped parentheses
    '\(MWh\)': r'\(MWh\)',  # Escaped parentheses
    'm2': r'm2',
    'MT CO2e': r'MT CO2e',
    '\(tCO2e\)': r'\(tCO2e\)',  # Escaped parentheses
    't CO2e': r't CO2e',
    'Kg CO2/m2': r'Kg CO2/m2',
    'tonns': r'tonns',
    'kgal': r'kgal',
    'MtCO2e': r'MtCO2e',
    'tCO2e': r'tCO2e',
    'lbs': r'lbs',
    'm3': r'm3',
    'kgCO2e/SF': r'kgCO2e/SF',
    'MtCO2e': r'MtCO2e',
    'tons': r'tons',
    '\(Megawatt Hours\)': r'\(Megawatt Hours\)',  # Escaped parentheses
    'megaliters\)': r'megaliters\)',  # Escaped parentheses
    '\(metric tons CO2e\)': r'\(metric tons CO2e\)',  # Escaped parentheses
    'Metric Tons\)': r'Metric Tons\)', # Escaped parentheses
    'metric ton CO2e':r'metric ton CO2e',
    'kgCO2-e/sqm': r'kgCO2-e/sqm'
}

def extract_and_standardize_units(text):
    unit_patterns = {
        # ... [keep existing patterns] ...
        'tonnes CO2-e': r'tonnes CO2-e',  # Adding the exact unit pattern for CO2
        # ... [keep existing patterns] ...
    }

    unit = ''
    for standard_unit, unit_pattern in unit_patterns.items():
        if re.search(unit_pattern, text, re.IGNORECASE):
            unit = standard_unit
            break

    return unit


# Modify the process_excel_file function
def process_excel_file(excel_file, question_column, raw_text):
    # Load the Excel file into a pandas DataFrame
    df = pd.read_excel(excel_file)

    # Extract the questions from the specified column
    questions = df[question_column].tolist()

    # Initialize chatbot components
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=800,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(raw_text)
    embeddings = OpenAIEmbeddings()
    document_search = FAISS.from_texts(texts, embeddings)
    #chain = load_qa_chain(OpenAI(), chain_type="stuff")
    #chain = load_qa_chain(OpenAI(), chain_type="stuff")
    chain = load_qa_chain(OpenAI(model_name="gpt-3.5-turbo-instruct"), chain_type="stuff")
    
    
    # Initialize lists to store extracted quantities and units
    quantities = []
    units = []
    answers = []  # Initialize the 'answers' list

    # Process each question and obtain the answers from the chatbot
    for question in questions:
        docs = document_search.similarity_search(question)
        answer = chain.run(input_documents=docs, question=question)

        # Extract and standardize quantity and unit from the answer
        quantity = extract_quantities(answer)
        unit = extract_and_standardize_units(answer)

        # Append to the respective lists
        quantities.append(quantity)
        units.append(unit)
        answers.append(answer)  # Append the answer to the 'answers' list

    # Add the answers, quantities, and units as new columns in the DataFrame
    df['Answers'] = answers
    df['Quantity'] = quantities
    df['Unit'] = units

    # Save the modified DataFrame back to the Excel file
    df.to_excel(excel_file, index=False)

def main():
    st.title('Spectreco Chatbot File Processing')

    # File inputs
    pdf_file = st.file_uploader('Upload PDF File', type='pdf')
    excel_file = st.file_uploader('Upload Excel File', type=['xlsx', 'xls'])
    question_column = st.text_input('Enter the column name for questions in the Excel file')

    # Process files on button click
    if st.button('Process Files'):
        if pdf_file is not None and excel_file is not None:
            # Process PDF file and extract raw text
            raw_text = process_pdf_file(pdf_file)

            # Process Excel file using chatbot
            process_excel_file(excel_file, question_column, raw_text)

            # Download the processed Excel file
            st.download_button('Download Processed Excel', data=excel_file.getvalue(), file_name=excel_file.name)
        else:
            st.warning('Please upload both a PDF and an Excel file.')
    llm = OpenAI(model="text-davinci-004")  # Update the model name here
    chain = load_qa_chain(llm, chain_type="stuff")
if __name__ == '__main__':
    main()










