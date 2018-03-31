**Parsing Pattern Generator**

Parsing Pattern Generator is a tool for quick addition of new parsing patterns to the program.

**Parsing patterns:**

Every parsing pattern consists of the following fields:

-	Pattern generator version
This field displays the version of the generator that created the record for this particular pattern. It is implemented for backwards compatibility so that if we change parsing mechanism and/or required fields, the program will know that it needs to apply one of the old approaches for this particular pattern. 
-	Platform name
This field describes the name of the conferencing platform to be used. This field is present because different platforms may have different ways of joining calls, for example, some platforms may require a dual-tone signal to choose language before entering conference PIN. Therefore, knowing platform name is essential.
-	Platform identifier
This field contains the key sequence of symbols that, if detected, allows us to accurately determine what platform will be used in the call. Most conferencing platforms’ invitations use the same template, allowing us to set platform identifier to some part of invitation text (often explicitly  containing platform’s name).
-	Field for analysis
This field defines which section of the .ics file is analyzed for relevant data. For version 1.0, two possible choices are DESCRIPTION and LOCATION.
-	Number format
This field describes the format in which phone number is written, as there may be some differences, such as presence of + before the number or brackets around a section of the number (although as of 13.10.17 format with brackets is ignored for now).
-	PIN identifier
This field contains the character sequence that precedes the PIN code, such as “PIN” of “Conference Code”. It is implemented so that the parser program knows exactly where in the text PIN is supposed to be located.
-	PIN
This field describes the format in which PIN code is written. As of 13.10.17, there are two possible formats: digit sequence and digit sequence with hash in the end.

All patterns are stored in the file patterns.txt, to which Pattern Generator can append new records (if *patterns.txt* is not present – generator creates one in its root directory). Below is an example of one of such entries:

[PATTERN]------------------------------------------
[VERSION] 1.0
[PLATFORM] Skype For Business
[PLATFORM IDENTIFIER] joinskypemeeting
[FIELD] DESCRIPTION
[NUMBER FORMAT] \+[0-9]+
[PIN IDENTIFIER] conferenceid
[PIN FORMAT] [0-9]+

Note that number and PIN formats are stored as regular expressions.

**How to use the program:**

 - On launch, the program automatically gets a list of all files in the */ics* directory and displays it on the right side of the window. To read information from one of the files, select in in the list and click “Open selected .ics file” button.
Contents of .ics file’s DESCRIPTION and LOCATION fields will be displayed in the large text field.

 - Before filling in pattern fields, press “Trim text” button to remove irrelevant characters from the text. Removed characters include spaces, minuses, percentage signs, parentheses and colons. All text is also converted to lowercase. This is done to simplify regular expressions used in the parsing process, however, format’s functionality allows parsing mechanics to change in subsequent versions if required.
Note that such transformed form is exactly how the parsing program “sees” the text when using corresponding version of the algorithm.

 - To fill pattern text fields, you have several options. First option is to select a portion of the text directly in the text field and press the corresponding button to the left of the pattern section, for example, “Platform Identifier”. Second option is just copy-pasting relevant data into corresponding fields, as they are enabled for editing. Third option is to enter data manually.

 - When all fields are filled, press “ADD PATTERN TO THE LIST” button to append a new record with the data you selected to the patterns.txt file.

**Important points for filling in data:**

 - No PIN required for the conference:

	If PIN is not required for the conference, please leave default values for PIN identifier and PIN fields, so that the generator creates a correct record

 - Platform identifier not present:

	In some cases, only a phone number and PIN are present in the LOCATION field. In that case, leave the default value in the PLATFORM IDENTIFIER field.
