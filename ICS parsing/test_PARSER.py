"""
Testing script for the .ics contents extractor, has built-in test cases for different conferencing platforms and parsing patterns

"""

import PARSER
import json
import os

def MakeTests():
    
   # listOfICS = os.listdir("icsTests")
    listOfICS = [s for s in os.listdir("icsTests") if s.endswith('.ics')]
    listOfJson = []
    for item in listOfICS:
        listOfJson.append(item.replace(".ics",".txt"))
    for source in listOfICS:
        print(source)
        det = PARSER.ParseICS("patterns.txt", os.path.join("icsTests", source))
        with open(os.path.join("icsTests", source.replace(".ics",".txt")), 'w') as outfile:
            outfile.write(json.dumps(det))

def test_PARSER():
    
    expectedV = []
    actualV = []
    
    listOfICS = [s for s in os.listdir("icsTests") if s.endswith('.ics')]
    listOfJson = []
    for item in listOfICS:
        listOfJson.append(item.replace(".ics",".txt"))
    
    for item in listOfJson:
        with open(os.path.join("icsTests", item), 'r') as file:
            entry = json.load(file)
            expectedV.append(entry)
    
    for f in listOfICS:
        det = PARSER.ParseICS("patterns.txt", os.path.join("icsTests", f))
        actualV.append(det)
        
    i = 0
    for expected, actual in zip(expectedV, actualV):
        print("NOW CHECKING: " + listOfICS[i])
        i += 1
        assert expected == actual
    

