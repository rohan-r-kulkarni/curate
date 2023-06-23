import requests
import json
from bs4 import BeautifulSoup
from py2neo import Graph
from py2neo.data import Node, Relationship
from py2neo.ogm import *
from getpass import getpass
import argparse
import sys
from graphdb_client import GraphClient
import re

SECRETS = True

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download from CULPA, upload to CUrate"
    )
    parser.add_argument(
        "-u",
        "--user",
        type=str,
        help="Neo4j Username"
    )
    parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="Neo4j Password"
    )
    
    return parser.parse_args(args=None if sys.argv[1:] else ["--help"])

def pprint(obj):
    print(json.dumps(obj, indent=2))

if __name__ == "__main__":
    
    if SECRETS:
        import secrets
        USERNAME = secrets.user
        PASSWORD = secrets.pw
    else:
        args = get_args()

        USERNAME = args.user
        if USERNAME is None:
            USERNAME = "neo4j"
        PASSWORD = args.password
        if USERNAME and PASSWORD is None:
            PASSWORD = getpass("Enter Password: ")



    graph = GraphClient("neo4j+s://38ed1ee0.databases.neo4j.io", USERNAME, PASSWORD)


    prof_review_endpoint = "api/review/get/professor/"

    #create professors
    depts = graph.get_dept_dict()
    # for k, dept in depts.items():
    #     profs = graph.get_culpa_professors_by_dept(k)

    #     for prof in profs:
    #        graph.create_professor(prof["firstName"], prof["lastName"], dept, culpa_id = prof["professorId"])

    #create courses
    dept_issues = []
    for k, dept in depts.items():
        courses = graph.get_culpa_courses_by_dept(k)
        issue_list = []

        for course in courses:
            #make courseCode atomic
            
            course_code = course["courseCode"]
            if course_code is None:
                issue_list.append(course)
                continue
            splitted = course_code.split(" ")
            dept4 = re.compile(r'[A-Z]{4}')

            if len(splitted) == 2 and dept4.search(splitted[0]): #normal
                course_depts = splitted[0]
                code = splitted[1]
            else:
                issue_list.append(course)
            
            if len(issue_list) > 0:
                dept_issues.append({"dept":dept, "dept_culpa_id":k, "course_issues":issue_list})

            course_name = course["courseName"]
            course_name = course_name.strip().replace("\"", "")

            try:
                graph.create_course(course_depts, code, course_name, culpa_id = course["courseId"])
            except RuntimeError:
                print(course)


    with open("issues/orphan_courses.json", "w") as issue_file:
        json.dump(dept_issues, issue_file, indent=2)

    