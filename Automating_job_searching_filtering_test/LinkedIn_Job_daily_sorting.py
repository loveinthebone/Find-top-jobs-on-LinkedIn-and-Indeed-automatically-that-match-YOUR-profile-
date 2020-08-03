# -*- coding: utf-8 -*-
"""
Created on Thursday Jul 16 2020
Modified on Aug 03 2020

@author: Kingson Zhou
"""

# In[] Import required libraries
# import PyPDF2
# import textract
import re
import string
import csv
from datetime import datetime
import os

# In[] Main function
def main():
    # Path of this script
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    
    # Define a "digital me" dictionary, which includes keywards that describe my soft skills, work experience, and job perferences
    digital_me = word_me()

    # Score the job posts scraped today, score them according to the similarity to the digital me, 
    # and sort the posts according to the total matching score
    scored_job_posts = score_sort_posts(digital_me, script_dir)
    
    # Save the sorted job posts data, together with the scores
    save_scored_posts(scored_job_posts, script_dir)

    # Open the top 5 matching job posts in the default browser
    open_top_posts(scored_job_posts)

# In[] Build a word cloud representing me
def word_me():

    digital_me = {
            'soft skills':['creativity','innovation','concept','think outside the box','creative','proactive',
                                'organized', 'planning','plan','independent','listener','analytical','innovative','improvement',
                                'result-driven','enthusiasm','supportive','quality','optimize'
                                ],      
            
            'mechanical':['solidworks','inventor','autocad','machine','device',
                                    'machinery','maintenance','manufacture','machining','mechanics','precision',
                                    'mechanical','production','design',
                                    'concept','process','material','strength','fatigue','failure analysis',
                                    'stamp','punching','sensor','electronics','microcontroller','arduino','driver',
                                    'motor','coil','vibration','acoustic','strength','motion', 'piezo','piezoelectric','electric',
                                    'root cause', 'actuator','prototypes','equipment','mechanical engineer','project engineer',
                                    'desugn engineer','system','tolerance','technician', 'drawings','feasibility','product','products','testing',
                                    '3d modeling','automation','handson','testing','testing','testing','pwm','pid','technology'],
            
            'researcher':['photoacoustic','optics','light','interferometers','interferometer','interferometry',
                            'technology','photonic','optical','spectroscopy','equipment','development','research',
                            'sensor','sensors', 'data analysis','python', 'theory','proposal',
                            'matlab','comsol','labview','acoustic','sensitive','stability',
                            'response time','linearity','sensing','temperature','pressure','fiber','laser',
                            'near infrared','power transformer','co2','iot','device',
                            'material','validation','prototypes','data processing','physical ','feasibility ','measurement',
                            'setup','theoretical','boundary','applied physics', 'phd','experiments','literature','publication',
                            'conference','characterization','analysis','absorption','experiment','nir','wavelength',
                            'modulation','intensity','amplifier','signal','rd' #R&D, NIR
                            ,'noise','techniques','microscope','metrology','measurements','scientist', 'complex','postdoc',
                            'modeling', 'academic','thermal','scientific','gas','calibration'],
            
            'simulation':['comsol','finite element analysis','fea','fem','acoustic','simulation',
                                'modeling','thermal','vibration','amplitude','deformation','strength','modeling',
                                'python'],

            'best':['gas','sensor','photoacoustic','power transformer', 'absorption','spectroscopy', 'miniaturization', 'miniaturized','fiber optics','comsol'],
            
            'impossible':['professor','phd','internship']
            }
    return digital_me


# In[] open the job posts csv file, save posts information to a list
def unpack_file(file_abs_path, date_string):
    data_list = []

    with open(file_abs_path, newline='', encoding="utf-8") as csvfile:
        datareader = csv.reader(csvfile)
        for row in datareader:
            if row[2] != date_string:
                continue
            else:
                data_list.append(row)
    return data_list

# # Test:
# file_path = r'e:/Python3732/Scripts/web_scraping/daily_job_scraping_Kingson.csv'
# dateString = datetime.strftime(datetime.now(), '%Y_%m_%d') # date of today
# # print(dateString)
# date_string = dateString
# test = unpack_file(file_path,dateString)[0:3]


# In[] Compare the description string with the word cloud string, output score
def compare(post, digital_me):
    description = post[4]
   
    # Convert all strings to lowercase
    text = description.lower()
    # Remove numbers
    text = re.sub(r'\d+','',text)
    # Remove punctuation
    text = text.translate(str.maketrans('','',string.punctuation))

    title = post[0]
    title = re.sub(r'\d+','',title)
    title_text = title.lower().translate(str.maketrans('','',string.punctuation))

    # Initialize a scores list and variables to save scores for different area
    scores =[]
    soft_skills = 0
    Mechanical_engineer = 0
    researcher = 0
    simulation = 0
    best = 0
    impossible = 0 # impossible words are those I don't want to have in the job post

    # Obtain the scores for each area
    for area in digital_me.keys():
            
        if area == 'soft skills':
            for word in digital_me[area]:
                if word in text:
                    soft_skills +=1
            scores.append(soft_skills)
            
        elif area == 'mechanical':
            for word in digital_me[area]:
                if word in text:
                    Mechanical_engineer +=1
            scores.append(Mechanical_engineer)
            
        elif area == 'researcher':
            for word in digital_me[area]:
                if word in text:
                    researcher +=1
            scores.append(researcher)
            
        elif area == 'simulation':
            for word in digital_me[area]:
                if word in text:
                    simulation +=1
            scores.append(simulation)
            
        elif area == 'best':
            for word in digital_me[area]:
                if word in text:
                    best +=10
            scores.append(best)
            
        else:
            for word in digital_me[area]:
                if word in title_text:
                    impossible -= 100
            scores.append(impossible)

    # Also add a column of total scores    
    score_sum = sum([impossible, best, simulation, researcher, Mechanical_engineer, soft_skills])
    scores.append(score_sum)

    return scores

# # Test:
# description = """How will your job look as Team Lead / Mechatronics Designer?
# In our product development projects at R&D you and your team take responsibility for a unit or module in our products. You are focusing with your team on mechatronic topics like accurate positioning, media handling, fast and accurate motion or thermal control.

# Together with architects you specify and agree on requirements based on customer’s demands. After this you and your team to come up with technical designs and concepts that meet these objectives, properly balancing time, quality, performance, interdisciplinary interactions and taking cost into account.

# Within the project you collaborate with colleagues from other disciplines than mechanics and electronics, like embedded software and also chemistry and physics, who are mainly responsible for the ink and print head development. Together you review the ideas and jointly develop smart creative solutions that meet the overall project objectives. You test and review your model based design(s) by building prototypes to proof the feasibility of the routes you have identified.

# """
# test1 = compare(description, word_me())

# In[] Score descriptions according to the word cloud, and extend it to the list:
def update_list(data_list, digital_me):
    for post in data_list:
        score = compare(post, digital_me) # score is single number list, or a list of scores in different domain, and their sum
        post.extend(score)
    return data_list

# In[] score and sort posts
def score_sort_posts(digital_me, script_dir):
    # path for the job posts data
    rel_path = r"data/Linkedin_job_posts_daily.csv"
    path = os.path.join(script_dir, rel_path)

    date_string = datetime.strftime(datetime.now(), '%Y_%m_%d') # date of today

    data_list = unpack_file(path, date_string)
    scored_job_posts = update_list(data_list, digital_me)
    scored_job_posts.sort(key=lambda x:-x[-1]) #sort by the total score descend.
    return scored_job_posts

# In[] save sorted posts
def save_scored_posts(scored_job_posts, script_dir):
    rel_path = r"data/Linkedin_job_posts_daily_scored.csv"
    new_file_path = os.path.join(script_dir, rel_path)
    file_exists = os.path.isfile(new_file_path)
    with open(new_file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["job_title", "job_company", "search_date",  "job_url", "description", "SOFT_SKILL", "MECHANICS", "RESEARCHER", "SIMULATION", "BEST", "IMPOSSIBLE", "TOTAL_SCORE"])
        writer.writerows(scored_job_posts)
    print("job posts sorting finished!")
#In[] open the top job posts in browser
def open_top_posts(scored_job_posts):
    import webbrowser
    import time
    #  c = webbrowser.get('C:/Program Files/Mozilla Firefox/firefox.exe %s') 
    for i in range(5):
        try:
            # os.startfile(scored_job_posts[i][3])

            webbrowser.open(scored_job_posts[i][3], new=1)
            
            # c.open(scored_job_posts[i][3], new=1)
            time.sleep(1)
        except:
            continue

# In[] run it
if __name__ == "__main__":
    main()