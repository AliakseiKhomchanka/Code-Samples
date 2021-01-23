# Github status reporter for TeamCity builds

This a script that was used as en emergency measure when the status reporting for TeamCity started failing without any apparent reason and all investigations weren't showing any clues. For the entire duration of the investigation, this script was basically a complete replacement to the bundled GitHub status reporting plugin in TeamCity that was running independently in AWS Lambda with a CRON-scheduled trigger and as such was not affected by whatever internal problems TeamCity was having, only connected to TC itself via several API calls (which remained operational).

The script consists of two parts:

1. The status reporting script itself
2. Another CRON-triggered script that was monitoring a separate PR set up specifically to track failures of the TeamCity status reporting plugin

More detailed information about scripts is in corresponding folders.