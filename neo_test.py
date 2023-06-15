from py2neo import Graph
from py2neo.data import Node, Relationship
from py2neo.ogm import *
from getpass import getpass

password = getpass()

graph = Graph("neo4j+s://38ed1ee0.databases.neo4j.io", auth=("neo4j", password), secure=True)


result = graph.run('CREATE (o: Object {name: "obj"})')
print(result)

# r = Node("Person", name="Rohan")
# graph.create(r)
