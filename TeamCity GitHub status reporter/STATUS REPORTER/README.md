# Status reporter

This script handles status reports to GitHub avoiding TeamCity's own infrastructure. All processing of build summaries, filtering etc. is done in an AWS Lambda function at fixed intervals.

## Why it was necessary

At some unfortunate point, the GitHub reporting plugin in TeamCity started ignoring builds at random, i.e. for ten hours everything is ok - and then no build statuses are reported for hours, after which the plugin mysteriously goes back to normal. With no visible changes to TC configuration or underlying infrastructure in the change history and seemingly no errors in logs, an investigation was being carried out. However, anticipating possible delays in the resolution of the problem, a plan B has been proposed, consisting of a script running on a schedule in AWS Lambda that would take over status reporting until the underlying issue has been resolved.

## Why it worked

Simply put, it worked because it had nothing to do with the part of TeamCity was failing. All of the script's logic was running outside of TeamCity, only fetching build lists and configurations via TeamCity API, which, luckily, was working normally (if it wasn't, status reporting probably would've been the least of our concerns). From there, is was just some filtering and ordering of build info plus a handful of GitHub API calls.

## How it worked

Every N minutes the script fetches lists of builds that were scheduled, running or completed within N+1 minutes (an overlap of time windows to ensure that no build fall through the cracks, it's better to report the same status for the same build twice than to not report it at all). After that, it goes through each build configuration ID. Some build configuration IDs may have several builds for the same SHA in the same time window (i.e. when someone restarts the build) so old builds must be discarded and only the newest one for a particular SHA must remain for each build type ID. 

In the process of going through each build type ID, the script also fetches configuration for the GitHub reporting plugin (the one that broke) and fetches the information regarding the location where the status needs to be reported (mainly the GitHub status context).

While fetching all relevant data, the script also automatically resolves all %PARAMETER references (recursively, in case parameters resolve to other %PARAMETER fields).

## Limitations

The script makes an assumption that each build configuration has only one VCS root. If there are more - the script will get confused and won't know which repo to report status to. This can be fixed by some manually added clutches with special rules for particular build type IDs, not very elegant, but it works.

It is also theoretically possible to exhaust the GitHub API quota if there are too many builds to report (thus forcing a change in scheduling), but no such problems occured in reality so far.

## Parameters

Below are all the environment variables that the script expects to find:

**TC_USERNAME**: Username for TeamCity API calls

**TC_PASSWORD**: Password for TeamCity API calls

**TC_ENDPOINT**: TeamCity endpoint for APi calls in the format of `https://teamcity.domain:port` withput the trailing slash

**TIME_DELTA**: The time window in which the script looks for builds, set accordingly to the schedule + 1 or 2 minutes

**GH_TOKEN**: The token for GitHub API calls, used to publish actual statuses

## Closing notes

The script doesn't have unit tests as due to the very nature of the problem it was a one-time thing that doesn't need additional upgrades.