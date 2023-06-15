from py2neo import Graph
from py2neo.data import Node, Relationship
from py2neo.ogm import *
import requests
import json

class GraphClient():
    def __init__(self, url, username, password):
        self.db = Graph(url, auth=(username, password), secure=True)
        self.CULPA_URL = "https://culpa.info/"

    def run_query(self, query: str, **kwargs) -> dict:
        try:
            res = self.db.run(query)
        except:
            raise RuntimeError
        
        return res

    def get_culpa_professors_by_dept(self, dept_id):
        dept_endpoint = self.CULPA_URL + "api/department/" + str(dept_id)
        dept_content = json.loads(requests.get(dept_endpoint).content)
        return dept_content["departmentProfessors"]

    def create_professor(self, first_name, last_name, department, culpa_id=None):
        create_prof_query = f"""
            CREATE (o: Prof {{
                                fname: {first_name},
                                lname: {last_name},
                                dept: {department},
                                culpa_id: {culpa_id}
                            }})
        """
        res = self.run_query(create_prof_query)
        return res