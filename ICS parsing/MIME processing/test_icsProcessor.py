"""
Test script for the .ics processor

"""

import re              # For regular expressions
import base64          # For decoding 64-bit encoded strings
import icsProcessor    # For parsing .ics files
import os              # For platform-independent path joiing

def test_Correspondence():
    with open("MIME/mail7bit") as f:
        input_normal = f.read()
    with open("MIME/mail64bit") as f:
        input_64 = f.read()
        
    with open("Mtests/expected_normal") as f:
        expected_normal = f.readlines()
    with open("Mtests/expected_64") as f:
        expected_64 = f.readlines()
    
    actual_normal = icsProcessor.findICS(input_normal)
    actual_64 = icsProcessor.findICS(input_64)
    
    expected_normal = [item.replace("\n","") for item in expected_normal]
    expected_64 = [item.replace("\n","") for item in expected_64]
    
    assert expected_normal == actual_normal
    assert expected_64 == actual_64

def prepareTest(filepath):
        relevant = []
        separator = ''
        flag = False
        
        with open(filepath) as f:
            aslist = f.readlines()
        
        for item in aslist:
            if re.search('boundary=', item):
                separator = re.search("boundary=\".*",item)
                separator = re.search("\".*\"",separator.group(0)).group(0).replace("\"","")
                break
        
        for item in aslist:
            if re.search("--", item) and flag == True:
                flag = False
                break
            if re.search('Content-Type: text/calendar',item):
                flag = True
            if flag == True:
                relevant.append(item)
        
        # Deleting non-.ics lines while checking if .ics file is encoded
        encoded64 = False
        if relevant:
            del relevant[0]
            if re.search('Content-Transfer-Encoding: base64',relevant[0]): 
                encoded64 = True
            else:
                encoded64 = False
            del relevant[0]
        else:
            return("Can't find any .ics data")
        
        if encoded64 == True:
            converted = []
            for item in relevant:
                converted.append(base64.b64decode(item).decode())
            relevant = ''.join(converted).split("\n")
        
        relevant = [item for item in relevant if item != "\r" and item != ""]
        relevant = [item.replace("\n","").replace("\r","") for item in relevant]
        
        return relevant

def makeTests():
    log_normal = prepareTest(os.path.join("MIME","mail7bit"))
    with open(os.path.join("Mtests","expected_normal"), "w") as f:
        f.writelines(log_normal)
    log_64 = prepareTest(os.path.join("MIME","mail64bit"))
    with open(os.path.join("Mtests","expected_64"), "w") as f:
        f.writelines(log_64)
        
