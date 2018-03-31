"""
Extraction of .ics files' content from MIME files

"""

import re         # For detection of .ics file markers
import base64     # For decoding of 64-bit encoded strings

def findICS(emailcontent):
    
    """
    This function takes a string with contents of the MIME file as input and returns a list of .ics file lines
    """
    
    relevant = []           # Lines from the .ics file
    separator = ''          # Separator for setions of the MIME file
    flag = False
    
    aslist = emailcontent.split("\n")
    
    # Extracting the correct separator
    for item in aslist:
        if re.search('boundary=', item):
            separator = re.search("boundary=\".*",item)
            separator = re.search("\".*\"",separator.group(0)).group(0).replace("\"","")
            break
    
    # Search through lines and after finding the .ics boundary, extract all relevant data
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
    
    # Decode .ics file if it was 64-bit encoded
    if encoded64 == True:
        converted = []
        for item in relevant:
            converted.append(base64.b64decode(item).decode())
        relevant = ''.join(converted).split("\n")
    
    # Cleaning up al the lines so that they would be readable by the .ics parser
    relevant = [item for item in relevant if item != "\r" and item != ""]
    relevant = [item.replace("\n","").replace("\r","") for item in relevant]
    
    return relevant