import re
import numpy as np
from numpy.linalg import norm
from gensim.models.doc2vec import Doc2Vec
from pdfminer.high_level import extract_text
import docx
import pytesseract
from PIL import Image
import sys
import os


def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_image(image_path):
    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_path)

    # Use pytesseract to perform OCR on the image
    text = pytesseract.image_to_string(image)

    return text

def preprocess_text(text):
    # Convert the text to lowercase
    text = text.lower()

    # Remove punctuation from the text
    text = re.sub('[^a-z]', ' ', text)

    # Remove numerical values from the text
    text = re.sub(r'\d+', '', text)

    # Remove extra whitespaces
    text = ' '.join(text.split())

    return text

def calculate_similarity(cv_text, jd_text):
    # Preprocess CV and JD
    input_CV = preprocess_text(cv_text)
    input_JD = preprocess_text(jd_text)

    # Model evaluation
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, 'matching_service','cv_job_maching.model')
    model = Doc2Vec.load(model_path)
    v1 = model.infer_vector(input_CV.split())
    v2 = model.infer_vector(input_JD.split())
    similarity = 100 * (np.dot(np.array(v1), np.array(v2))) / (norm(np.array(v1)) * norm(np.array(v2)))

    return similarity

def extract_text_from_resume(resume_path):
     if resume_path.endswith('.pdf'):
        return extract_text(resume_path)
     elif resume_path.endswith('.docx'):
        return extract_text_from_docx(resume_path)
     elif resume_path.endswith('.jpg'):
        return extract_text_from_image(resume_path)
     else:
        raise ValueError("Unsupported file format. Only PDF and DOCX files are supported.")

    


def matching(pdf_path, descr):
    text = extract_text_from_resume(pdf_path)
    similarity = calculate_similarity(text, descr)
    print('your similarity is',similarity )
    return similarity

# def matching(pdf_path, descr):
#     # text = extract_text_from_resume(pdf_path)
#     # similarity = calculate_similarity(text, descr)
#     similarity=0
#     return similarity




# # # # # if __name__ == "__main__":
# # # # #     resume_cv_path = 'C:/Users/pc/Desktop/Stage_PULSE/codes/ATS-PROJECT/ATS_PROJECT/ATS_Project/candidates/matching_service/data-scientist-resume-example.pdf'

# # # # #     description = """
# # # # Senior Data Scientist - Digital Government


# # # # Oracle Digital Government group is on a mission to support national governments on their digital transformation journey. If you have experience bringing AI models to production, and cloud knowledge, and/or have a passion for , we would like to hear from you. We are expanding our dedicated team so come join us on this exciting journey.


# # # # We are searching for an experienced Data Scientist to:


# # # #     Use machine learning, data mining, statistical techniques and others to create actionable, meaningful, and scalable solutions to solve complex government challenges
# # # #     Identify meaningful insights from complex data sources; interpret and communicate insights and findings to engineering teams and leadership
# # # #     Collaborate with engineering to build pipelines and tools for data ingestion, feature engineering, model training, model deployment and improvement.
# # # #     Establish scalable, efficient, automated processes to boost team productivity, such as model development, model validation and model implementation.





# # # # Responsibilities:


# # # #     Work closely with business teams and customers to understand business requirements, and implement new data science driven insights.
# # # #     Work with other Engineers to validate that data from internal and external sources is relevant, trustworthy and actionable and ensure platform provides required data and level of granularity for advanced Data Science projects to augment Cloud applications and provide Management Insights.
# # # #     Design and implement algorithms, train models, and operationalize models to production for ingestion by other SaaS services and continuously improve models. Experience with Python is required.
# # # #     Design innovative predictive models, optimization models, experiments and model performance testing.
# # # #     Address business/customer problems and questions using statistical and data science techniques to achieve business goals and KPI's. Come up with innovative solutions to address tradeoffs or challenges faced by teams.
# # # #     Perform ad hoc and in-depth analyses and then surface/report insights through dashboards & visualizations. Experience with Analytics tools such as Oracle Analytics Cloud (OAC) or Tableau
# # # #     Provide proactive leadership, demonstrating self-sufficiency, influencing and team building skills while creating and socializing innovative data science driven solutions.





# # # # Qualifications:

# # # #     Python (NumPy, Pandas, Scikit-learn, Keras, Flask)
# # # #     SQL (MySQL, Postgres)
# # # #     Git
# # # #     Time Series Forecasting
# # # #     Productionizing Models
# # # #     Recommendation Engines
# # # #     Customer Segmentation
# # # #     AWS
# # # # WORK EXPERIENCE

# # # # Data Scientist
# # # # Grubhub
# # # # June 2018 - Current | Princeton, NJ

# # # #     Developed and deployed a recommendation engine to production, leveraging past order history to conditionally recommend other menu items, resulting in a 7% increase in average order size.
# # # #     Implemented various time series forecasting techniques to predict surge in orders, reducing customer wait time by 10 minutes.
# # # #     Designed and piloted a model to increase incentives for drivers during peak hours, resulting in a 22% increase in driver availability.
# # # #     Led a team of 3 data scientists to model the ordering process in 5 unique ways, reported results, and made recommendations to increase order output by 9%.

# # # # Data Scientist
# # # # Spectrix Analytical Services
# # # # March 2016 - June 2018 | Princeton, NJ

# # # #     Built a customer attrition random forest model that improved monthly retention by 12 basis points for clients likely to opt-out by providing relevant product features for them.
# # # #     Coordinated with the product and marketing teams to determine interactions resulting in maximized service opt-ins, increasing conversions by 18%.
# # # #     Partnered with product team to create a production recommendation engine in Python, improving the length on-page for users, resulting in $225K in incremental annual revenue.
# # # #     Compiled and analyzed data surrounding the prototypes for a prosthesis, saving over $1M in its creation.

# # # # Entry-Level Data Analyst
# # # # Avenica
# # # # April 2015 - March 2016 | Mount Laurel, NJ

# # # #     Collaborated with product managers to perform cohort analysis, identifying an opportunity to reduce pricing by 21% for a segment of users, boosting yearly revenue by $560,000.
# # # #     Constructed operational reporting in Tableau to improve scheduling contractors, saving $90,000 in the annual budget.
# # # #     Implemented a long-term pricing experiment that improved customer lifetime value by 23%.
# # # #     Ran, submitted, and reported on monthly client enrollments, services opted in for, and the employees assigned to clients.


# # # # # """
# # # # # score_matching = main(resume_cv_path, description)
# # # # # formatted_score = "{:.2f}".format(score_matching)
# # # # # print(formatted_score)

