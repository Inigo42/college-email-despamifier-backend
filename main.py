import requests
from bs4 import BeautifulSoup


URL = 'https://academicinfluence.com/schools?country=United+States+of+America'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')


discipline_options_els = soup.find(id='discipline-select').find_all('option')


discipline_options = []

for el in discipline_options_els:
    discipline_options.append(el.text.lower().replace(' ', '-').strip())



for discipline in discipline_options:
    for i in range(0, 91):
        DISCIPLINE_URL = 'https://academicinfluence.com/schools?country=United+States+of+America&discipline=' + discipline + '&page=' + str(i)
        discipline_page = requests.get(DISCIPLINE_URL)
        college_per_discipline_soup = BeautifulSoup(discipline_page.content, 'html.parser')
        all_college_items = college_per_discipline_soup.find_all('div', class_='school-card')
        for college_item in all_college_items:
            #region Desirability, Infuelence, Name, Rank
            rank = college_item.find('div', class_='school-card__rank').text.replace('#', '').strip()
            school_name = college_item.find('h2', class_='school-card__school-name').text.strip()
            influence_el = college_item.find('div', class_='school-card__world-rank')
            desirability_el = college_item.find('div', class_='school-card__desirability-rank')
            influence = ''
            desirability = ''
            if influence_el != None:
                influence = influence_el.text.replace('#', '').replace('overall school desirability', '').strip()
            if desirability_el != None:
                desirability = desirability_el.text.replace('#', '').replace('overall school desirability', '').strip()
            # endregion


            # #region Tution, Acceptence, Graduation, Student Body, Median SAT, Median ACT
            main_info_container = college_item.find('div', class_='school-card__stats')
            
            item_info_containers = main_info_container.find_all('div', class_='school-card__stat')
            info = []
            for item in item_info_containers:
                ind_info = item.find_all('p')
                info.append({'desc': ind_info[0].text.strip(), 'info': ind_info[1].text.strip()})
                
            # #endregion
            

            # #region Link to Profile, Location
            middle_div_link_container = college_item.find('div', class_='school-card__bar')


            profile_btn_link = middle_div_link_container.find('a', href=True)['href']            
            location_el = middle_div_link_container.find('div', class_='school-card__city-label')
            location = '?'
            if location_el != None:
                location = location_el.text.strip()
            print(location)
            #endregion
        
        all_colleges = []


    
    