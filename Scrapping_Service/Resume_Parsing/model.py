# imports
import spacy
from spacy.matcher import PhraseMatcher

from pdfminer.high_level import extract_text
import re
import json

# load default skills data base
from skillNer.general_params import SKILL_DB
# import skill extractor
from skillNer.skill_extractor_class import SkillExtractor

# init params of skill extractor
nlp = spacy.load("en_core_web_lg")
# init skill extractor
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

def get_sorted_skills_list(annotations):
    # Initialize a list to keep track of unique technical skills and their scores
    technical_skills = []
    technical_types = ["fullUni", "oneToken", "lowSurf"]

    # Iterate through full matches
    for match in annotations['results']['full_matches']:
        skill = match['doc_node_value']
        score = match['score']
        # Full matches are by default technical skills
        technical_skills.append((skill, score))

    # Iterate through n-gram scored matches
    for match in annotations['results']['ngram_scored']:
        skill = match['doc_node_value']
        score = match['score']
        skill_type = match['type']
        # Check if the skill is a technical skill based on type
        if skill_type in technical_types:
            technical_skills.append((skill, score))

    # Remove duplicate skills while keeping the highest score for each skill
    skill_score_dict = {}
    for skill, score in technical_skills:
        if skill not in skill_score_dict or skill_score_dict[skill] < score:
            skill_score_dict[skill] = score

    # Convert the dictionary back to a list of skills and sort them by score in descending order
    sorted_technical_skills = sorted(skill_score_dict.items(), key=lambda x: x[1], reverse=True)

    # Extract the list of skills from the sorted list of tuples
    sorted_skills_list = [skill for skill, score in sorted_technical_skills]

    return sorted_skills_list


def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_name_from_resume(text):
    name = None

    # Use regex pattern to find a potential name
    # Pattern handles both cases: all uppercase or first letter uppercase
    pattern = r"\b([A-Z]+(?:\s[A-Z]+)+)\b|\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b"
    match = re.search(pattern, text)
    if match:
        name = match.group()
        if name:
            return name
        else:
            return "Name not found"
    else:
        "Name not found"

def extract_contact_number_from_resume(text):
    # Use regex pattern to find a potential contact number
    # The pattern starts with '+' or '0' and captures all following digits and separators
    # while ensuring there are at least 8 digits in the phone number.
    pattern = r"\b(?:\+|\d)(?:\d[-.\s]?){7,14}\d\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()
        if contact_number:
            return '+'+(contact_number)
        else:
            return"Contact Number not found"

    return "Contact Number not found"

def extract_email_from_resume(text):
    email = None

    # Use regex pattern to find a potential email address
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()
        if email:
            return email
        else:
            return"Email not found"
    else:
        "Email not found"

def get_technical_skills_list(text):
    annotations = skill_extractor.annotate(text)
    sorted_technical_skills_list = get_sorted_skills_list(annotations)
    return sorted_technical_skills_list

def extract_education(text):
    list_degrees_names = """
Ph.D..*
PhD.*
Doctoral Degree.*
doctoral degree.*
Doctorat.*
Doctorat.*
doctorat.*
Doctorate.*
Cycle d'Ingénieur.*
cycle d'ingénieur.*
Diplôme d'Ingénieur.*
diplôme d'ingénieur.*
Master of Arts.*
Master of Science.*
Master's Degree.*
Master's degree.*
Master.*
Mastère Spécialisé.*
mastère spécialisé.*
MBA.*
mba.*
BAC+5.*
Bac+5.*
BAC+4.*
Bac+4.*
BAC+3.*
Bac+3.*
Bachelor's Degree.*
Bachelor's degree.*
Licence.*
licence.*
Professional Degree.*
professional degree.*
Advanced Degree.*
advanced degree.*
Advanced Diploma.*
advanced diploma.*
Preparatory Cycle.*
Preparatory cycle.*
Cycle Préparatoire.*
Cycle préparatoire.*
Diplôme d'Études Supérieures Spécialisées.*
diplôme d'études supérieures spécialisées.*
Diplôme Universitaire de Technologie.*
DUT.*
DUT.*
Diplôme Universitaire.*
diplôme universitaire.*
BAC+2.*
Bac+2.*
Agrégation.*
agrégation.*
Associate Degree.*
associate degree.*
Bac Pro.*
bac pro.*
BAC.*
Baccalauréat.*
baccalauréat.*
Bachelor of Arts.*
Bachelor of Science.*
Bachelor.*
Brevet d'Études Professionnelles.*
brevet d'études professionnelles.*
Brevet de Technicien Supérieur.*
brevet de technicien supérieur.*
Certificat d'Aptitude Professionnelle.*
certificat d'aptitude professionnelle.*
Certificat d'Études Secondaires.*
certificat d'études secondaires.*
Certificate.*
certificate.*
DESS.*
Diploma.*
diploma.*
GED.*
General Educational Development.*
High School Diploma.*
high school diploma.*
Postgraduate Certificate.*
postgraduate certificate.*
Postgraduate Diploma.*
postgraduate diploma.*
Vocational Certificate.*
vocational certificate.*
"""
    # Join degree names into a regular expression pattern using alternation
    pattern = "|".join(list_degrees_names.strip().split("\n"))
    # Find all matches in the input text using the regex pattern and MULTILINE flag
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    # Output the matches
    return matches
# profil extracting & classification ###############################################################3

import sys
import os
from sklearn.preprocessing import LabelEncoder
import pickle
from joblib import load
from CustomTransformer import CustomTransformer

def extract_profil(skills_list):
    import warnings
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
    # loaded_model = load('C:/Users/pc/Desktop/Stage_PULSE/codes/ATS-PROJECT/ATS_PROJECT/ATS_Project\Scrapping_Service/Resume_Parsing/classification_model_gridsearch.joblib')

    # Construct the relative path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    classification_model_path = os.path.join(base_dir, 'Resume_Parsing', 'classification_model_gridsearch.joblib')

    # Debugging: Print the constructed path
    print(f"Constructed model path: {classification_model_path}")

    # Load the model using the constructed relative path
    loaded_model = load(classification_model_path)

    skills_text = ", ".join(skills_list)
    # Load the fitted label encoder
    label_encoder_path = os.path.join(base_dir, 'Resume_Parsing', 'label_encoder.pkl')

    # Debugging: Print the constructed path
    print(f"Constructed model path: {label_encoder_path}")
    with open(label_encoder_path, 'rb') as le_file:
        encoder = pickle.load(le_file)

    # Predict the label for the test text
    predicted_label = loaded_model.predict([skills_text])[0]

    # Decode the predicted label to get the corresponding category
    predicted_category = encoder.inverse_transform([predicted_label])[0]

    # Print the predicted category
    # print("Predicted category:", predicted_category)
    return predicted_category


def Resume_Parsing(path):
    try:
        text_Extracted = extract_text_from_pdf(path)
        name = extract_name_from_resume(text_Extracted)
        phone = extract_contact_number_from_resume(text_Extracted)
        email = extract_email_from_resume(text_Extracted)
        skills = get_technical_skills_list(text_Extracted)
        educations = extract_education(text_Extracted)
        profil = extract_profil(skills)

        resume_data = {
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Skills": skills,
            "Education": educations,
            "Profil": profil
        }

        # Convert dictionary to JSON string
        json_data = json.dumps(resume_data, indent=4)
        return json_data

    except Exception as e:
        # Handle or log the exception as needed
        return f"An error occurred: {str(e)}"


# with open('resume_data.json', 'w') as json_file:
#         json.dump(extracted_data, json_file, indent=4)

# def Resume_Parsing_Dataset(path):
#     try:
#         text_Extracted = extract_text_from_pdf(path)
#         skills = get_technical_skills_list(text_Extracted)
#         skill_data = ' '.join(skills)
#         return skill_data
    

#     except Exception as e:
#         # Handle or log the exception as needed
#         return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    path_resume = 'C:/Users/pc/Desktop/Stage_PULSE/codes/Emails Scrapping/Resume_Parsing/ouajil_younes_cve.pdf'
    result = Resume_Parsing(path_resume)
    print(result)








    # import os
    # import pandas as pd

    # # Create an empty DataFrame
    # df = pd.DataFrame(columns=['Skill', 'Type'])

    # # Define the folder path and skill type
    # folder_path = 'C:/Users/pc/Desktop/proper_Data/Devops'
    # skill_type = 'Devops'

    # # Iterate over the PDF files in the folder
    # for file_name in os.listdir(folder_path):
    #     if file_name.endswith('.pdf'):  # Check if the file is a PDF file
    #         try:
    #             # Parse the resume and extract skills
    #             text = extract_text_from_pdf(os.path.join(folder_path, file_name))
    #             skills = get_technical_skills_list(text)
    #             skill_data = ' '.join(skills)
                
    #             # Append the extracted skills and type to the DataFrame
    #             df = df._append({'Skill': skill_data, 'Type': skill_type}, ignore_index=True)
    #         except Exception as e:
    #             # Log the error and continue to the next file
    #             print(f"Error processing file '{file_name}': {e}")
    #             continue

    # # Save the DataFrame to a CSV file
    # df.to_csv('skills_devops.csv', index=False)

    # print("Skills extracted and saved to skills.csv")
