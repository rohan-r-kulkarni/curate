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

    def get_culpa_reviews_by_prof_id(self, prof_id):
        review_endpoint = self.CULPA_URL + "api/review/get/professor/" + str(prof_id)
        review_content = json.loads(requests.get(review_endpoint).content)
        return review_content["reviews"]

    def parse_culpa_review(self, review_obj):
        if type(review_obj) == str:
            review_obj = json.loads(review_obj)
        rev_id = review_obj["reviewId"]
        del review_obj["reviewId"]
        del review_obj["reviewType"]
        course_name = review_obj["reviewHeader"]["courseName"]
        del review_obj["reviewHeader"]
        review_obj["date"] = review_obj.pop("submissionDate")
        return rev_id, course_name, json.dumps(review_obj)

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

    def create_department(self, dept_name, dept_code=None, culpa_id=None):
        create_dept_query = f"""
            MERGE (o: Dept {{
                                name: "{dept_name}",
                                code: "{dept_code}",
                                culpa_id: "{culpa_id}"
                            }})
        """
        res = self.run_query(create_dept_query)
        return res
    
    def relate_course_dept(self, course_name, dept_name):
        relate_course_dept_query = f"""
            MATCH (d: Dept), (c: Course) 
                WHERE d.name = "{dept_name}" AND c.name = "{course_name}" 
            MERGE (d)-[: hasCourse]->(c) 
            RETURN c,d 
        """
        res = self.run_query(relate_course_dept_query)
        return res
    
    def create_student(self, username):
        create_student_query = f"""
            MERGE (o: Student {{
                                username: "{username}",
                                review_count: 0
                            }})
        """
        res = self.run_query(create_student_query)
        return res
    
    def relate_student_course(self, username, course_name):
        relate_student_course_query = f"""
            MATCH (s: Student), (c: Course) WHERE s.username="{username}" AND c.name="{course_name}"
            MERGE (s)-[: hasTaken]->(c) RETURN s,c;
        """
        res = self.run_query(relate_student_course_query)
        return res

    def relate_student_prof(self, username, prof_first_name, prof_last_name):
        relate_student_prof_query = f"""
            MATCH (s: Student), (p: Prof) WHERE s.username="{username}" AND p.fname = "{prof_first_name}" AND p.lname="{prof_last_name}"
            MERGE (s)-[: hasHad]->(p) RETURN s,p;
        """
        res = self.run_query(relate_student_prof_query)
        return res

    def create_review(self, username, prof_first_name, prof_last_name, course_name, review, culpa_id=None):
        """
        The review object should be JSON-like string that contains unpackable information such as:
        content, workload, date
        from CULPA: deprecated, votes (likes, dislikes, funny, count)
        Stored in graph DB as a JSON-like object
        """
        review.replace("\"", "\"\"\"")
        review.replace("\"", "\"\"\"")
        create_review_query = f"""
            MERGE (r: Review {{
                student_reviewer: "{username}",
                prof_fname: "{prof_first_name}",
                prof_lname: "{prof_last_name}",
                course_name: "{course_name}",
                info: '{review}',
                culpa_id: "{culpa_id}"
            }})
        """
        res = self.run_query(create_review_query)
        return res