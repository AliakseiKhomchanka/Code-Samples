"""
This module contains tools for parsing .ics files using patterns predefined by a Pattern Generator
"""

from icalendar import Calendar, Event, Timezone
import re
import pprint
import json

class ParsePattern:
    
    """Criteria for parsing relevant data"""
    
    platform = 'UNKNOWN'            # Platform corresponding to this parsing pattern
    platformExpr = 'DEFAULT'        # Regular expression that, if found, identifies the conferencing platform
    field = 'DEFAULT'               # Field of the ics file from which data is parsed
    numberFormat = 'DEFAULT'        # Regular expression specifying the number format
    pinID = 'DEFAULT'
    pin = 'DEFAULT'                 # Regular expression specifying the pin format
    
    def __repr__(self):
        repres = {}
        repres["PLATFORM"] = self.platform
        repres["PLATFORM EXPRESSION"] = self.platformExpr
        repres["FIELD"] = self.field
        repres["NUMBER FORMAT"] = self.numberFormat
        repres["PIN ID"] = self.pinID
        repres["PIN"] = self.pin
        return(str(repres))
    
def parse(text, pattern):
    
    """Parsing the string for relevant data according to criteria specified by the ParsePattern object"""
    
    # Returning right away if phone number is not parsable
    
    if pattern.numberFormat == 'NOT_PARSABLE':
        return("NOT_PARSABLE")
    
    # Otherwise proceeding with parsing
    
    result = {}
    text = text.lower().replace(' ','').replace('-','').replace(':','').replace('-','').replace('%','').replace('(','').replace(')','')     # Removing all "irrelevant" characters
    
    platform = "UNKNOWN"
    
    if pattern.platform != "N/A":
        buf = re.search(pattern.platformExpr, text)
        if buf is not None:
            if buf.group(0) is not None:
                platform = pattern.platform
            else:
                return("NOT_PARSABLE")
    else:
        platform = "UNKNOWN"
    
    buf = re.search(pattern.numberFormat, text)
    if buf is not None:
        if buf.group(0) is not None:
            number = buf.group(0)
    else:
        return("NOT_PARSABLE")
    
    if pattern.pin != "nopin":
        buf = re.search(pattern.pinID + pattern.pin, text)
        if buf is not None:
            pin = buf.group(0).replace(pattern.pinID, '')
        else:
            return("NOT_PARSABLE")
    else:
        pin = "NOPIN"
    
    result["PLATFORM"] = platform
    result["NUMBER"] = number
    result["PIN"] = pin
    
    return(result)

def readPatterns(filepath):
    
    """Reading parsing patterns from a file"""
    
    patternList = []
    
    with open(filepath, 'r') as file:
        
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        now = 0
        while now < len(lines):
            if(lines[now] == "[PATTERN]------------------------------------------"):
                #print("HELLO")
                patt = ParsePattern()
                now += 1
                if lines[now] == "[VERSION] 1.0":
                    #print("HELLO FROM INSIDE")
                    now += 1
                    patt.platform = lines[now].replace("[PLATFORM] ", '')
                    now += 1
                    patt.platformExpr = lines[now].replace("[PLATFORM IDENTIFIER] ", '')
                    now += 1
                    patt.field = lines[now].replace("[FIELD] ", '')
                    now += 1
                    patt.numberFormat = lines[now].replace("[NUMBER FORMAT] ", '')
                    now += 1
                    patt.pinID = lines[now].replace("[PIN IDENTIFIER] ", '')
                    now += 1
                    patt.pin = lines[now].replace("[PIN FORMAT] ", '')
                    now += 1
                    patternList.append(patt)
            else:
                #print("WHY ERROR")
                patternList.append("PARSING ERROR")
           
     
    return(patternList)    

def determineData(filepath, patternlist):
    
    """Parses an .ics file with %filepath% according to the parsing pattern list %patternlist%"""
    
    eventData = {}    # A dictionary for relevant call data
    
    with open(filepath, 'rb') as file:
        cal = Calendar.from_ical(file.read())
    subComps = cal.subcomponents   
    for item in subComps:
        # If subcomponent is an event
        if type(item) is Event:
                        
            ###########################################################
            #        Parsing participants, time and meeting id        #
            ###########################################################
            
            organizer = item['ORGANIZER']
            scheduled_at = item['DTSTART']
            uid = item['UID']
            attendeeList = []
            if type(item['ATTENDEE']) is not list:
                attendeeList.append([item['ATTENDEE'].params['CN'], bytes.decode(item['ATTENDEE'].to_ical()).lower().replace('mailto:','')])
            else:               
                for att in item['ATTENDEE']:
                    attendeeList.append([att.params['CN'], bytes.decode(att.to_ical()).lower().replace('mailto:','')])           
            eventData['ORGANIZER'] = [
                    organizer.params['CN'],
                    bytes.decode(organizer.to_ical())
                         .lower()
                         .replace('mailto:','')]
            eventData['ATTENDEES'] = attendeeList
            eventData['START'] = bytes.decode(scheduled_at.to_ical())
            eventData['UID'] = bytes.decode(uid.to_ical())
            
            ###########################################################
            #              PARSING PHONE NUMBER AND PIN               #
            ###########################################################
            
            possibleData = []                                # A list of all parsing results for different platforms
            finalCallData = None
            for pattern in patternlist:
                if pattern.field == "LOCATION" or pattern.field == "N/A":
                    possibleData.append(parse(item["LOCATION"], pattern))
                elif pattern.field == "DESCRIPTION":
                    possibleData.append(parse(item["DESCRIPTION"], pattern))
            
            if not possibleData:
                eventData["CALL_DATA"] = "NOT_PARSED"
                return eventData
            
            ###########################################################
            #      Determining which set of parsed data is correct    #
            ###########################################################

            # Removing all NOT_PARSABLE elements
            while "NOT_PARSABLE" in possibleData:
                possibleData.remove("NOT_PARSABLE")

            # Checking if there are entries with a detected platform
            
            dataWithPlatform = []
            for entry in possibleData:
                if entry["PLATFORM"] != "UNKNOWN":
                    dataWithPlatform.append(entry)
            
            # Checking whether a PIN is required for a chosen platform by checking all entries for this platform
            
            if dataWithPlatform:
                finalCallData = dataWithPlatform[0]
                if dataWithPlatform[0]["PIN"] == "NOPIN" and len(dataWithPlatform)>1:
                    for entry in dataWithPlatform:
                        if entry["PLATFORM"] == dataWithPlatform[0]["LOCATION"] and entry["PIN"] != "NOPIN":
                            finalCallData = entry      

            if not possibleData:
                eventData["CALL_DATA"] = "NOT_PARSED"
                return eventData
            
            # If no platform match was found - take first unknown platform
            
            if not finalCallData:
                finalCallData = possibleData[0]
            
            eventData["CALL_DATA"] = finalCallData
            return eventData
            
        # If subcomponent is a pattern    
        if type(item) is Timezone:
            eventData['TIMEZONE'] = str(item['TZID'])
    
        
def ParseICS(patternsfile, icsfile):
    """Parse the .ics file according to the pattern file"""
    pats = readPatterns(patternsfile)
    determined = determineData(icsfile, pats)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(determined)
    return(determined)

# For testing purposes

def MakeTests():
    
    toWrite = []
    
    testFileList = ["ics/SKYPE 1.ics",
                "ics/SKYPE 2.ics",
                "ics/GOTOMEETING.ics",
                "ics/UBER.ics",
                "ics/WEBEX.ics",
                "ics/ZOOM.ics",
                "ics/ZOOM 2.ics",
                "ics/PHONE NUMBER.ics"
                ]
    
    print("MADE TESTS: \n\n")
    
    for f in testFileList:
        det = ParseICS("patterns.txt", f)
        print(json.dumps(det) + "\n\n")
        toWrite.append(json.dumps(det))
    
    with open("Tests.txt", 'w') as file:
        for item in toWrite:
            file.write(item + "\n")



































