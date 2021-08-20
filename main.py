import requests
from bs4 import BeautifulSoup


URL = 'https://academicinfluence.com/schools?country=United+States+of+America'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')


discipline_options_els = soup.find(id='discipline-select').find_all('option')


discipline_options = []

for el in discipline_options_els:
    discipline_options.append(el.text.lower().strip().replace(' ', '-').strip())

all_colleges = []


for discipline in discipline_options:
    for i in range(0, 1): # change to 91 when looking for full data
        DISCIPLINE_URL = 'https://academicinfluence.com/schools?country=United+States+of+America&discipline=' + discipline + '&page=' + str(i)
        discipline_page = requests.get(DISCIPLINE_URL)
        college_per_discipline_soup = BeautifulSoup(discipline_page.content, 'html.parser')
        all_college_items = college_per_discipline_soup.find_all('div', class_='school-card')
        for college_item in all_college_items:
            #region Desirability, Infuelence, Name, Rank
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
            # endregion


            # #region Tution, Acceptence, Graduation, Student Body, Median SAT, Median ACT
            main_info_container = college_item.find('div', class_='school-card__stats')
            
            item_info_containers = main_info_container.find_all('div', class_='school-card__stat')
            
            tuition = None
            acceptence = None
            grad_rate = None
            student_body = None
            sat = None
            act = None
            for item in item_info_containers:
                ind_info = item.find_all('p') 
                desc = ind_info[0].text.strip().lower().replace(" ", "")
                info = ind_info[1].text.strip().lower().replace(" ", "")
                if desc == 'tuition+fees':
                    tuition = int(info.replace('$', '').replace('k', '')) * 1000 # assuming colleges cost more than 1k
                elif desc == 'acceptance':
                    acceptence = int(info.replace('%', ''))/100
                elif desc == 'graduation':
                    grad_rate = int(info.replace('%', ''))/100
                elif desc == 'student\xa0body':
                    student_body = int(info.replace('$', '').replace('k', '').replace('<', '')) * 1000
                else:
                    split = info.split('/')
                    sat = int(split[0])
                    act = int(split[1])
                
            # #endregion

            # #region Link to Profile, Location
            middle_div_link_container = college_item.find('div', class_='school-card__bar')


            profile_btn_link = middle_div_link_container.find('a', href=True)['href']            
            location_el = middle_div_link_container.find('div', class_='school-card__city-label')
            
            
            city = None
            state = None
            if location_el != None:
                location = location_el.text.strip().split(',')
                city = location[0]
                state = location[1].strip()
            #endregion
            found_college = False
            for college in all_colleges:
                if college['slug'] == slug:
                    college[discipline + '_rank'] = rank
                    found_college = True
                    break
            
            
            if not found_college:
                all_colleges.append({
                    discipline + '_rank': rank,
                    'school_name': school_name,
                    'influence': influence,
                    'desirability': desirability,
                    'city': city,
                    'state': state,
                    'tuition': tuition,
                    'acceptence': acceptence,
                    'grad_rate': grad_rate,
                    'student_body': student_body,
                    'sat': sat,
                    'act': act,
                    'slug': slug
                })
    
    break # remove when not testing

