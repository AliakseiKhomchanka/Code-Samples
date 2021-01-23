# Github plugin crash detector

This script's purpose is to detect when the GitHub plugin crashes, after which the script fetches TeamCity server logs and sends them with the summary of the crash via an SNS channel.

## The purpose
---

As the company was investigating reasons for problems with the GitHub plugin, there was no way to predict when exactly the crash would occur next. As engineers couldn't constantly keep watch on TeamCity 24/7, a need for an automated crash detector arose. 

## How it worked
---

As TeamCity itself was not reporting any failures, a control PR has been set up instead with a CROn-triggered job in TeamCity that was posting a status update to that PR bia the faulty plugin every 10 minutes. The script, running in AWS Lambda every 10 minutes, was checking the HEAD commit of that PR for status updates. If the last status update was older than 10 minutes - that was an indicator of the plugin failing. In that case, the script would fetch TeamCity server logs, put logs in an S3 bucket, compose an email message with a crash summary and a link to the log file in S3 and send the email to all subscribers of the corresponding SNS topic. The script was tracking BOTH the plugin failing and coming back to life fetching server logs for both cases.

The current state of the plugin (BROKEN or HEALTHY) is recorded in environment variables of the function itself. The script rewrites the value whenever there's a status flip.

## Parameters
---

**TC_USERNAME**: Teamcity username

**TC_PASSWORD**: Teamcity password

**BUILD_INTERVAL**: The interval at which the control build is running

**TC_ENDPOINT**: Endpoint for TeamCity API calls in the `https://teamcity.domain:port` format

**TC_URL**: Url of your TeamCity server, it will be used to fetch server log files

**FUNCTION_ARN**: ARN of the function running the script

**SNS_ARN**: ARN of the SNS topic used to handle the mailing list

**REPO**: Repository in which the control PR is set up

**REF**: Commit SHA for which the status is being posted

**GH_TOKEN**: API token for GitHub API calls

**TC_STATUS**: Indicates whether the GitHub plugin is BROKEN or HEALTHY at the time