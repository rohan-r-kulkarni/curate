from py2neo import Graph
from py2neo.data import Node, Relationship
from py2neo.ogm import *
import requests
import json

class GraphClient():
    def __init__(self, url, username, password):
        self.db = Graph(url, auth=(username, password), secure=True)
        self.CULPA_URL = "https://culpa.info/"
        self.dept_dict = None

    def run_query(self, query: str, **kwargs) -> dict:
        try:
            res = self.db.run(query)
        except:
            raise RuntimeError
        
        return res
        
    def generate_dept_dict(self):
        if self.dept_dict is None: #not previously stored
            dept_info_endpoint = self.CULPA_URL + "api/department/all"
            dept_info = []
            for dept_let in json.loads(requests.get(dept_info_endpoint).content)["departments"]:
                dept_info.extend(dept_let["departmentsList"])
            depts = dict([tuple([obj["departmentId"], obj["departmentName"]]) for obj in dept_info])
            self.dept_dict = depts
        return self.dept_dict

    def get_dept_dict(self):
        return self.generate_dept_dict()

    def get_culpa_deptname_by_id(self, dept_id):
        return self.generate_dept_dict()[dept_id]

    def get_culpa_professors_by_dept(self, dept_id):
        dept_endpoint = self.CULPA_URL + "api/department/" + str(dept_id)
        dept_content = json.loads(requests.get(dept_endpoint).content)
        return dept_content["departmentProfessors"]

    def create_professor(self, first_name, last_name, department, culpa_id=None):
        create_prof_query = f"""
            MERGE (o: Prof {{
                                fname: "{first_name}",
                                lname: "{last_name}",
                                dept: "{department}",
                                culpa_id: {culpa_id}
                            }})
        """
        res = self.run_query(create_prof_query)
        return res
    
    def get_culpa_courses_by_dept(self, dept_id):
        dept_endpoint = self.CULPA_URL + "api/department/" + str(dept_id)
        dept_content = json.loads(requests.get(dept_endpoint).content)
        return dept_content["departmentCourses"]
    
    def create_course(self, course_dept, code, name, culpa_id=None):
        create_course_query = f"""
            MERGE (o: Course {{
                                course_dept: "{course_dept}",
                                code: "{code}",
                                name: "{name}",
                                culpa_id: {culpa_id}
                            }})
        """
        res = self.run_query(create_course_query)
        return res