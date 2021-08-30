## main.py
## Jimmy, Ray, and Jeremi @ Aug 2021
## Web Scraper + SQLite

import requests
from bs4 import BeautifulSoup
import json
from writing_utils import *

if __name__ == '__main__':
    URL = 'https://academicinfluence.com/schools?country=United+States+of+America'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')


    discipline_options_els = soup.find(id='discipline-select').find_all('option')


    discipline_options = []

    for el in discipline_options_els:
        discipline_options.append(el.text.lower().strip().replace(' ', '-').strip())

    all_colleges = [] # contains info for all colleges
    slug_dict = {} # contains college identifier info (slug) as keys and the index of the college in all_colleges as values


    for discipline in discipline_options:
        for i in range(0, 91): # change to 91 when looking for full data
            DISCIPLINE_URL = 'https://academicinfluence.com/schools?country=United+States+of+America&discipline=' + discipline + '&page=' + str(i)
            discipline_page = requests.get(DISCIPLINE_URL)
            college_per_discipline_soup = BeautifulSoup(discipline_page.content, 'html.parser')
            all_college_items = college_per_discipline_soup.find_all('div', class_='school-card')
            
            for college_item in all_college_items:
                #region : Desirability, Influence, Name, Rank
                rank = int(college_item.find('div', class_='school-card__rank').text.replace('#', '').strip())
                school_name = college_item.find('h2', class_='school-card__school-name').text.strip()
                slug = school_name.replace(' ', '-').lower()
                influence_el = college_item.find('div', class_='school-card__world-rank')
                desirability_el = college_item.find('div', class_='school-card__desirability-rank')
                influence = None
                desirability = None
                if influence_el != None:
                    influence = int(influence_el.text.replace('#', '').replace('institution\'s overall influence', '').strip())
                if desirability_el != None:
                    desirability = int(desirability_el.text.replace('#', '').replace('overall school desirability', '').strip())
                #endregion
                print(school_name)

                #region : Tuition, Acceptance, Graduation, Student Body, Median SAT, Median ACT
                main_info_container = college_item.find('div', class_='school-card__stats-inner')
                
                item_info_containers = main_info_container.find_all('div', class_='school-card__stat')
                tuition = None
                acceptance = None
                grad_rate = None
                student_body = None
                sat = None
                act = None
                
                for item in item_info_containers:
                    ind_info = item.find_all('p') 
                    desc = ind_info[0].text.strip().lower().replace(" ", "")
                    info = ind_info[1].text.strip().lower().replace(" ", "")
                    if desc == 'tuition+fees':
                        #(1) TUITION AND FEES
                        tuition = int(info.replace('$', '').replace('k', '')) * 1000 # assuming colleges cost more than 1k
                    elif desc == 'acceptance':
                        #(2) ACCEPTANCE RATE
                        acceptance = int(info.replace('%', ''))/100
                    elif desc == 'graduation':
                        #(3) GRADUATION RATE
                        grad_rate = int(info.replace('%', ''))/100
                    elif desc == 'student\xa0body':
                        #(4) STUDENT BODY SIZE
                        student_body = int(info.replace('$', '').replace('k', '').replace('<', '')) * 1000
                    else:
                        split = info.split('/')
                        #(5) SAT SCORE
                        sat = int(split[0])
                        #(6) ACT SCORE
                        act = int(split[1])
                # #endregion

                # #region : Link to Profile, Location, and Undergrad Size
                middle_div_link_container = college_item.find('div', class_='school-card__bar')

                profile_btn_link = middle_div_link_container.find('a', href=True)['href']
                profile_page = requests.get('https://academicinfluence.com' + profile_btn_link)       
                profile_soup = BeautifulSoup(profile_page.content, 'html.parser')
                contact_admissions_btn = profile_soup.find('a', class_='profile__button', href=True)
                contact_admissions_btn_link = None
                if contact_admissions_btn != None:
                    #(7) LINK TO COLLEGE ADMISSIONS WEBSITE
                    contact_admissions_btn_link = contact_admissions_btn['href']
                
                # create domain variable using contact_admissions_btn_link
                # this domain serves as a default in case the college is not found in the json file
                #(8) DOMAIN
                domain = None
                if contact_admissions_btn_link != None and '.edu' in contact_admissions_btn_link:
                    url_components = contact_admissions_btn_link.split(".edu")
                    domain = url_components[0].split('.')[-1] + ".edu"


                #use profile_soup to also extract undergrad student body size
                school_profile_stats = profile_soup.find_all('div', class_='school-profile__stat')

                undergrad_student_body = None 

                for stat_container in school_profile_stats:
                    stat_label = stat_container.find('p', class_='stat-label').text
                    if stat_label == 'Under-Grads':
                        #(9) UNDERGRAD STUDENT BODY SIZE
                        undergrad_student_body = int(stat_container.find('p', class_='stat').text.lower().strip().replace('k', '').replace('<', '')) * 1000


                location_el = middle_div_link_container.find('div', class_='school-card__city-label')
                city = None
                state = None
                if location_el != None:
                    location = location_el.text.strip().split(',')
                    #(10) CITY
                    city = location[0]
                    #(11) STATE
                    state = location[1].strip()


                if slug in slug_dict: #if college is already found in college list, add new discipline rank
                    all_colleges[slug_dict[slug]][discipline + '_rank'] = rank
                #skip if the college has no information
                elif not any([rank, school_name, influence, desirability, city, state, tuition, acceptance, grad_rate, student_body, undergrad_student_body, sat, act, contact_admissions_btn_link, domain]):
                    continue
                else: # if college not already in college_list, create new dictionary for that college
                    all_colleges.append({
                        discipline + '_rank': (i + 1) * rank,
                        'school_name': school_name,
                        'influence': influence,
                        'desirability': desirability,
                        'city': city,
                        'state': state,
                        'tuition': tuition,
                        'acceptance': acceptance,
                        'grad_rate': grad_rate,
                        'student_body': student_body,
                        'undergrad_student_body': undergrad_student_body,
                        'sat': sat,
                        'act': act,
                        'slug': slug,
                        'admissions_website': contact_admissions_btn_link,
                        'domain': domain
                    })

                    slug_dict[slug] = len(all_colleges)-1  # set slug key to correspond to the value of the index of the college in all_colleges
                
        break # remove when not testing 


    #### read JSON file and add official college domains to dictionaries ####
    with open('us_colleges.json', 'r') as f:
        college_data = json.load(f)

    for college in college_data:
        temp_slug = college["name"].replace(' ', '-').lower() #create temporary name for college
            
        if temp_slug in slug_dict: #check if college is in slug_dict
            try:
                all_colleges[slug_dict[temp_slug]]["domain"] = college["domains"][0] #add college domain info for each college
            except KeyError:
                continue #skip college if domain not found

    
    #print(all_colleges) # total 4454 colleges, each containing rankings for 25 disciplines


    #### write data to an SQLite file ####
    writeToSQLite(all_colleges, 'colleges.db')