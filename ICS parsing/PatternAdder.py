"""A tool for assisted creation of parsing patterns"""

from tkinter import *
from icalendar import Calendar, Event, Timezone
import re
import os

class App:
  def __init__(self, master):
    
    # Version of the pattern generator
    self.version = "1.0"
           
    frame = Frame(master)
    
    # Buffers for contents of DESCRIPTION and LOCATION fields of the .ics file
    self.descr = ""
    self.loc = ""
    
    # Initializing variables for pattern fields
    self.platform = r""
    self.platformID = r""
    self.field = r""
    self.number = r""
    self.pinID = r""
    self.pin = r""
    
    # Displaying the name of the file currently observed
    self.nowFile = StringVar()
    self.nowFile.set("FILENAME")
    self.selectedLabel = Label(frame, textvariable = self.nowFile)
    self.selectedLabel.grid(row = 0, column = 0, sticky = W)
    
    #Text field for contents of the ics file
    self.textfield = Text(frame)
    self.textfield.grid(row = 1, column = 0, sticky = W + E, columnspan = 3, rowspan = 1)
    
    # Getting a list of all .ics files and displaying it
    self.listOfFiles = os.listdir("ics")
    self.FileList = Listbox(frame)
    self.FileList.grid(row = 1, column = 4, sticky = W + E + N + S, columnspan = 1, rowspan = 1)
    for entry in self.listOfFiles:
        self.FileList.insert(END, entry)
    
    #Packing the frame
    frame.pack()
    
    # Buttons for actions
    
    self.plNameButton = Button(frame, text="Platform name", command=self.selectPlName)
    self.plNameButton.grid(row = 3, column = 0, sticky = W + E, padx = 10, pady = 5)
    self.plIDButton = Button(frame, text="Platform Identifier", command=self.selectPlID)
    self.plIDButton.grid(row = 4, column =0, sticky = W + E, padx = 10, pady = 5)
    self.field = Button(frame, text="Relevant field", command=self.selectField)
    self.field.grid(row = 5, column = 0, sticky = W + E, padx = 10, pady = 5)
    self.num = Button(frame, text="Number format", command=self.selectNumber)
    self.num.grid(row = 6, column = 0, sticky = W + E, padx = 10, pady = 5)
    self.pinID = Button(frame, text="PIN identifier", command=self.selectPinID)
    self.pinID.grid(row = 7, column = 0, sticky = W + E, padx = 10, pady = 5)
    self.pin = Button(frame, text="PIN format", command=self.selectPin)
    self.pin.grid(row = 8, column = 0, sticky = W + E, padx = 10, pady = 5)
    self.pin = Button(frame, text="ADD PATTERN TO THE LIST", command=self.addToList)
    self.pin.grid(row = 9, column = 0, sticky = W + E, padx = 10, pady = 5)
    
    # Buttons for working with ics files
    
    self.plNameButton = Button(frame, text="Open selected .ics file", command=self.openICS)
    self.plNameButton.grid(row = 2, column = 0, sticky = W + E, padx = 10, pady = 5)
    self.plNameButton = Button(frame, text="Browse for .ics file", command=self.openICS)      # TO IMPLEMENT
    self.plNameButton.grid(row = 2, column = 1, sticky = W + E, padx = 10, pady = 5)
    self.plNameButton = Button(frame, text="Trim text", command=self.trimICS)
    self.plNameButton.grid(row = 2, column = 2, sticky = W + E, padx = 10, pady = 5)
    
    
    # Editable text boxes for parsing pattern fields
    
    self.plNameText = Entry(frame)
    self.plNameText.grid(row = 3, column = 1, sticky = W + E, padx = 10, pady = 5, columnspan = 3)
    self.plIDText = Entry(frame)
    self.plIDText.grid(row = 4, column = 1, sticky = W + E, padx = 10, pady = 5, columnspan = 3)
    self.fieldText = Entry(frame)
    self.fieldText.grid(row = 5, column = 1, sticky = W + E, padx = 10, pady = 5, columnspan = 3)
    self.numText = Entry(frame)
    self.numText.grid(row = 6, column = 1, sticky = W + E, padx = 10, pady = 5, columnspan = 3)
    self.pinIDText = Entry(frame)
    self.pinIDText.grid(row = 7, column = 1, sticky = W + E, padx = 10, pady = 5, columnspan = 3)
    self.pinText = Entry(frame)
    self.pinText.grid(row = 8, column = 1, sticky = W + E, padx = 10, pady = 5, columnspan = 3)
    
    # Setting default values for text fields
    
    self.plNameText.insert(0, "N/A")
    self.plIDText.insert(0, "N/A")
    self.fieldText.insert(0, "N/A")
    self.numText.insert(0, "N/A")
    self.pinIDText.insert(0, "N/A")
    self.pinText.insert(0, "nopin")
    
   # Functions for grabiing data from selected portions of the text
  
  def selectPlName(self):
    self.plNameText.delete(0, END)
    self.platform = self.textfield.selection_get()
    self.plNameText.insert(0, self.platform)
    
  def selectPlID(self):
    self.plIDText.delete(0, END)
    self.platformID = self.textfield.selection_get()
    self.plIDText.insert(0, self.platformID)
    
  def selectField(self):
    self.fieldText.delete(0, END)
    self.field = self.textfield.selection_get()
    self.fieldText.insert(0, self.field)
    
  def selectNumber(self):
    self.numText.delete(0, END)
    self.number = self.textfield.selection_get()
    self.numText.insert(0, self.number)
    
  def selectPinID(self):
    self.pinIDText.delete(0, END)
    self.pinID = self.textfield.selection_get()
    self.pinIDText.insert(0, self.pinID)
    
  def selectPin(self):
    self.pinText.delete(0, END)
    self.pin = self.textfield.selection_get()
    self.pinText.insert(0, self.pin)
  
  # Function that makes transforms values in pattern fields to be written into the file
  
  def summarize(self):
    self.platform = self.plNameText.get()
    self.platformID = self.plIDText.get()
    self.field = self.fieldText.get()
    self.number = self.numText.get()
    self.pinID = self.pinIDText.get()
    self.pin = self.pinText.get()
    
    # Determining a regular expression for number
    notParsed = True
    if re.search(r'\+[0-9]+', self.number) is not None and notParsed == True:
        self.number = '\+[0-9]+'
        notParsed = False
    if re.search(r'[0-9]+', self.number) is not None and notParsed == True:
        self.number = '[0-9]+'
        notParsed = False
    if notParsed == True:
        self.number = "NOT_PARSABLE"

    
    # Determining a regular expression for PIN
    notParsed = True
    if re.search(r'[0-9]+#', self.pin) is not None and notParsed == True:
        self.pin = '[0-9]+#'
        notParsed = False
    if re.search(r'[0-9]+', self.pin) is not None and notParsed == True:
        self.pin = '[0-9]+'
        notParsed = False
    if self.pin.lower() == "nopin" and notParsed == True:
        self.pin = 'NO_PIN'
        notParsed = False
    if notParsed == True:
        self.pin = "NOT_PARSABLE"

    
  def addToList(self):
    """Appends the parsing pattern to the list"""
    self.summarize()
    with open("patterns.txt", 'a') as file:
        file.write("[PATTERN]------------------------------------------\n"+
                   "[VERSION] " +
                   self.version +
                   "\n" +
                   "[PLATFORM] "+
                   self.platform+
                   "\n"+
                   "[PLATFORM IDENTIFIER] "+
                   self.platformID+
                   "\n"+
                   "[FIELD] "+
                   self.field+
                   "\n"+
                   "[NUMBER FORMAT] "+
                   self.number+
                   "\n"+
                   "[PIN IDENTIFIER] "+
                   self.pinID+
                   "\n"+
                   "[PIN FORMAT] "+
                   self.pin+
                   "\n")
    
  def openICS(self):
    """Opens an .ics file and displays contents of DESCRIPTION and LOCATION fields"""
    filepath = os.path.join("ics", self.FileList.get(self.FileList.curselection()))
    self.nowFile.set(filepath)
    with open(filepath, 'rb') as file:
        cal = Calendar.from_ical(file.read())  
    subComps = cal.subcomponents 
    for item in subComps:
        # If subcomponent is an event
        if type(item) is Event:
            self.textfield.delete(1.0, END)
            self.descr = item['DESCRIPTION']
            self.textfield.insert(END, "\n\n\nDESCRIPTION:\n\n\n")
            self.textfield.insert(END, self.descr)
            self.loc = item['LOCATION']
            self.textfield.insert(END, "\n\n\nLOCATION:\n\n\n")
            self.textfield.insert(END, self.loc)
            
  def trimICS(self):
    """Removes irrelevant characters from text"""
    self.textfield.delete(1.0, END)
    self.textfield.insert(END, "\n\n\nDESCRIPTION:\n\n\n")
    self.textfield.insert(END, self.descr.lower().replace(' ','').replace('-','').replace(':','').replace('-','').replace('%','').replace('(','').replace(')',''))
    self.textfield.insert(END, "\n\n\nLOCATION:\n\n\n")
    self.textfield.insert(END, self.loc.lower().replace(' ','').replace('-','').replace(':','').replace('-','').replace('%','').replace('(','').replace(')',''))          
  

root = Tk()
root.title("Parsing Pattern Generator")
app = App(root)
root.mainloop()