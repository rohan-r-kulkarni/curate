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
    
    args = get_args()

    USERNAME = args.user
    if USERNAME is None:
        USERNAME = "neo4j"
    PASSWORD = args.password
    if USERNAME and PASSWORD is None:
        PASSWORD = getpass("Enter Password: ")



    graph = GraphClient("neo4j+s://38ed1ee0.databases.neo4j.io", USERNAME, PASSWORD)


    prof_review_endpoint = "api/review/get/professor/"

    depts = graph.get_dept_dict()
    for k, dept in depts.items():
        profs = graph.get_culpa_professors_by_dept(k)

        for prof in profs:
           graph.create_professor(prof["firstName"], prof["lastName"], dept, culpa_id = prof["professorId"])

    