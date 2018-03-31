# Conference call data parser

This folder contains source codes for a conference call data parser. Conference invites arrive by email and therefore have to first be processed by a MIME parser to extract icalendar file data, after which the .ics file itself is parsed for relevant information.

## Provided modules

1. A MIME parser for extraction of .ics data from MIME files
2. An .ics parser for extraction of call data
3. Pytest-compatible test scripts for both parsers
4. An editor for parsing patterns, allows different "generations" of parsing patterns in case there is a need to check different text patterns for the same conferencing platform

Some files (particularly, MIME and .ics samples) are omitted for the sake of privacy as they contain personal data of third parties.