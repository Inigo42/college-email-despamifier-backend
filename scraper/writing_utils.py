## utils.py
## Jimmy and Jeremi @ Aug 2021
## Utility functions for writing college data

import csv
import sqlite3

print("writing_utils.py is loaded")

#### Option 1: writing to a CSV file ####
def writeToCSV(college_list, file_name):
    with open(file_name, "w") as file:
        writer = csv.writer(file)

        headers = ['school_name', 
                'slug', 
                'acceptance', 
                'city', 
                'state',
                'grad_rate',
                'desirability',  
                'influence', 
                'overall_rank', 
                'sat', 
                'act',
                'student_body',
                'undergrad_student_body',
                'tuition',
                'domain']

        writer.writerow(headers)

        for college in college_list:
            writer.writerow([
                college['school_name'],
                college['slug'],
                college['acceptance'],
                college['city'],
                college['state'],
                college['grad_rate'],
                college['desirability'],
                college['influence'],
                college['overall_rank'],
                college['sat'],
                college['act'],
                college['student_body'],
                college['undergrad_student_body'],
                college['tuition'],
                college['domain']
            ])
        

#### Option 2: writing to an SQLite file ####
def writeToSQLite(college_list, database):
    con = sqlite3.connect(database)

    cur = con.cursor()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS colleges (
            school_name text, 
            slug text,
            acceptance real,
            city text, 
            state text,
            grad_rate real, 
            desirability integer,
            influence integer, 
            overall_rank integer, 
            sat integer, 
            act integer, 
            student_body integer, 
            undergrad_student_body integer,
            tuition integer,
            domain text
        );"""
    )

    con.commit()

    for college in college_list:
        acceptance = college["acceptance"]
        act = college["act"]
        city = college["city"]
        desirability = college["desirability"]
        grad_rate = college["grad_rate"]
        influence = college["influence"]
        overall_rank = college["overall_rank"]
        sat = college["sat"]
        school_name = college["school_name"]
        slug = college["slug"]
        state = college["state"]
        student_body = college["student_body"]
        undergrad_student_body = college["undergrad_student_body"]
        tuition = college["tuition"]
        domain = college["domain"]


        # city, desirability, grad_rate, influence, overall_rank, sat, school_name, slug, state, student_body, tuition
        command_str = f"""INSERT INTO colleges VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        
        try:
            cur.execute(
                command_str, 
                [school_name, slug, acceptance, city, state, grad_rate, desirability, influence, overall_rank, sat, act, student_body, undergrad_student_body, tuition, domain]
                )
            con.commit()
        except Exception as e:  
            print(e)

    con.close()