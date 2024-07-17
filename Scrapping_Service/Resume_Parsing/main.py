# import mysql.connector
# from mysql.connector import Error 
import json

import os
import sys
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from model import Resume_Parsing
from CustomTransformer import CustomTransformer
def connect_insert(data, subject, reference, id_internship):
    # try:
        # # Connection parameters - adjust as necessary
        # connection = mysql.connector.connect(
        #     host='localhost',
        #     user='root',
        #     password='',
        #     database='resumedata'
        # )
        
        # if connection.is_connected():
        #     db_Info = connection.get_server_info()
        #     print("Connected to MySQL Server version ", db_Info)
        #     cursor = connection.cursor()
            
            # # Insert data into the Intern table
            # insert_query = """INSERT INTO Intern (name, email, phone, profil, skills, education, subject, reference, id_internship) 
            #                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            # record = (data['Name'], data['Email'], data['Phone'], data['Profil'], ', '.join(data['Skills']), '; '.join(data['Education']), subject, reference, id_internship)
            # cursor.execute(insert_query, record)
            # connection.commit()
    from utils.models import Intern

    intern = Intern(
                name=data['Name'],
                email=data['Email'],
                phone=data['Phone'],
                skills=data['Skills'],
                education=data['Education'],
                reference=reference,
                subject=subject,
                id_internship=id_internship,
                profil=data['Profil']

        )
    intern.save()
            
    print("Data inserted successfully into Intern table")
            
    # except Error as e:
    #     print("Error while connecting to MySQL", e)
    # finally:
    #     if connection.is_connected():
    #         cursor.close()
    #         connection.close()
    #         print("MySQL connection is closed")


def Resume_Parsing_to_DB(path, subject, reference, id_internship):
    json_data = Resume_Parsing(path) 
    print(json_data)
    data = json.loads(json_data)
    connect_insert(data,subject, reference, id_internship)

# if __name__ == '__main__':
#     subject = "Internship_2024"
#     reference = 'internsdksj'
#     id_internship = 'xx'
#     path_resume = 'C:/Users/pc/Desktop/Stage_PULSE/codes/Emails Scrapping/Resume_Parsing/ouajil_younes_cve.pdf'
#     Resume_Parsing_to_DB(path_resume,subject, reference, id_internship)

# #  usage
# if __name__ == '__main__':
    # folder_path = 'C:/Users/pc/Desktop/Emails Scrapping/Temporary_Attachments'
    # for filename in os.listdir(folder_path):
    #     if filename.endswith('.pdf'):  
    #         resume_path = os.path.join(folder_path, filename)
    #         Resume_Parsing_to_DB(resume_path)
    # subject = "Internship_2024"
    # reference = 'internsdksj'
    # id_internship = 'xx'
    # path_resume = 'C:/Users/pc/Desktop/Stage_PULSE/codes/Emails Scrapping/Resume_Parsing/ouajil_younes_cve.pdf'
    # Resume_Parsing_to_DB(path_resume,subject, reference, id_internship)

            


# with open('resume_data.json', 'w') as json_file:
#         json.dump(json_data, json_file, indent=4)


