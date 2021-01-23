import requests
import os
import json
from datetime import datetime, timedelta
import re
import copy


def lambda_handler(event, context):
    # Teamcity credentials
    username, password = os.environ.get("TC_USERNAME"), os.environ.get("TC_PASSWORD")
    endpoint = os.environ.get("TC_ENDPOINT")
    # Timing parameters to filter builds
    interval_mins = os.environ.get("TIME_DELTA")
    now = datetime.utcnow()
    earliest_build_timestamp = now - timedelta(minutes=int(interval_mins))
    earliest_build_timestamp = earliest_build_timestamp.strftime("'%Y%m%dT%H%M%S'")
    now = now.strftime("'%Y%m%dT%H%M%S'")
    print("NOW: " + str(now))
    print("EARLIEST BUILD TIMESTAMP: " + str(earliest_build_timestamp))
    print("TIME DELTA: " + str(interval_mins) + " MINUTES")

    # Fetch all builds in TC, whether they're in queued, running or finished state
    headers = {'Content-Type': 'application/xml',
               'Accept': 'application/json'}

    # Fetch queued builds
    url = endpoint + "/httpAuth/app/rest/builds/?locator=state:queued,branch:default:any,queuedDate:(date:{timestamp},condition:after)".format(
        timestamp=earliest_build_timestamp).replace("\'", "")
    response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
    response_json = json.loads(response.text)
    queued_builds = copy.deepcopy(response_json["build"])
    while response_json.get("nextHref", None) and response_json["count"] == 100:
        url = endpoint + response_json["nextHref"]
        response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
        response_json = json.loads(response.text)
        queued_builds.extend(response_json["build"])
    print(str(len(queued_builds)) + " QUEUED BUILDS")

    # Fetch running builds
    url = endpoint + "/httpAuth/app/rest/builds/?locator=state:running,branch:default:any,startDate:(date:{timestamp},condition:after)".format(
        timestamp=earliest_build_timestamp).replace("\'", "")
    response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
    response_json = json.loads(response.text)
    running_builds = copy.deepcopy(response_json["build"])
    while response_json.get("nextHref", None) and response_json["count"] == 100:
        url = endpoint + response_json["nextHref"]
        response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
        response_json = json.loads(response.text)
        running_builds.extend(response_json["build"])
    print(str(len(running_builds)) + " RUNNING BUILDS")

    # Fetch finished builds
    url = endpoint + "/httpAuth/app/rest/builds/?locator=state:finished,branch:default:any,finishDate:(date:{timestamp},condition:after)".format(
        timestamp=earliest_build_timestamp).replace("\'", "")
    response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
    response_json = json.loads(response.text)
    finished_builds = copy.deepcopy(response_json["build"])
    while response_json.get("nextHref", None) and response_json["count"] == 100:
        url = endpoint + response_json["nextHref"]
        response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
        response_json = json.loads(response.text)
        finished_builds.extend(response_json["build"])
    print(str(len(finished_builds)) + " FINISHED BUILDS")

    # Sum all fetched builds
    builds = queued_builds + running_builds + finished_builds
    build_info_list = []  # Info for processed builds will go here
    repeats = 0  # A counter for builds that were dropped as outdated. Not necessary, just for analysis.

    # If any disqualifying detail is discovered about a build type (like absence of a status context) - ignore it further
    bad_list = []
    ignore_list = [] # List of BuildTypeIDs that need to be ignored

    builds = [build for build in builds if build["buildTypeId"] not in ignore_list]

    for build in builds:
        web_url = build["webUrl"]
        # The big list only returns some fields from builds themselves, so we fetch more detailed info
        url = endpoint + build["href"]
        response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
        build_info = json.loads(response.text)
        if build_info["buildTypeId"] in bad_list:
            # print("DISQUALIFIED BUILD TYPE ID, SKIPPING")
            continue
        if build_info["buildTypeId"] in ignore_list:
            print("BUILD TYPE ID IN IGNORE LIST, SKIPPING")
            continue

        # Print timing data
        if build_info["state"] == "finished":
            timestamp_data = build_info["finishDate"].split("+")[0]
        if build_info["state"] == "queued":
            timestamp_data = build_info["queuedDate"].split("+")[0]
        if build_info["state"] == "running":
            timestamp_data = build_info["startDate"].split("+")[0]
        print("BUILD TIMESTAMP " + timestamp_data + " STATE: " + build_info["state"] + " URL:" + build_info["webUrl"])

        # Extract commit details -------------------------------------------------------------------------------------------
        commit = None
        revisions = build_info["revisions"]
        if revisions["count"] > 0:
            for revision in revisions["revision"]:
                try:
                    commit = revision["version"]
                except Exception as e:
                    print("EXCEPTION: " + str(e))
        # ------------------------------------------------------------------------------------------------------------------

        # Determine the timestamp for when the build was queued, started or finished
        if build["state"] == "finished":
            timestamp_data = build_info["finishDate"].split("+")[0]
        if build["state"] == "queued":
            timestamp_data = build_info["queuedDate"].split("+")[0]
        if build["state"] == "running":
            timestamp_data = build_info["startDate"].split("+")[0]
        timestamp = datetime.strptime(timestamp_data, '%Y%m%dT%H%M%S')
        # Check if a newer version of this build has already been added, if yes - discard the current build and go to the next one on the list
        existing_builds = [build for build in build_info_list if
                           build["type_id"] == build_info["buildTypeId"] and build["commit"] == commit]
        if existing_builds:
            if timestamp < existing_builds[0]["timestamp"]:
                print("A NEWER BUILD FOR CONFIGURATION " + build_info[
                    "buildTypeId"] + " AND COMMIT " + commit + " ALREADY EXISTS WITH TIMESTAMP OF " + str(
                    existing_builds[0]["timestamp"]))
                repeats += 1
                continue

        # Fetch the build type config (not information about the build itself, but the general build configuration)
        build_type_id = build_info["buildTypeId"]
        url = endpoint + "/app/rest/buildTypes/id:{id}".format(id=build_type_id)
        response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
        build_config = json.loads(response.text)

        # Extract build context. For that, we access build features and find the context in teh feature that forwards statuses (the one that always breaks)
        # Some jobs don't have status forwarding or have a broken context (lke a reference to a non-existent parameter) so we skip such builds
        context = None
        url = endpoint + "/app/rest/buildTypes/id:{id}/features".format(id=build_type_id)
        response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
        features = json.loads(response.text)
        if features["count"] == 0:
            print("BUILD TYPE ID" + build_info["buildTypeId"] + "DISQUALIFIED: NO GITHUB CONTEXT")
            bad_list.append(build_info["buildTypeId"])
            continue
        for feature in features["feature"]:
            if feature["type"] == "teamcity.github.status":
                properties = feature["properties"]["property"]
                for property in properties:
                    if property["name"] == "guthub_context":
                        context = property["value"]
                        break
            if context:
                break
        if not context:
            print("CONTEXT NOT FOUND FOR BUILD TYPE " + build_type_id)
            print("BUILD TYPE ID" + build_info["buildTypeId"] + "DISQUALIFIED: NO GITHUB CONTEXT")
            bad_list.append(build_info["buildTypeId"])
            continue

        # Check if context has any %PARAMETER% references. Repeat until all parameter references are replaced with their values
        regex_pattern = "%.*%"
        match = re.search(regex_pattern, context)
        value = "somevalue"
        while match:
            value = None
            if build_config["parameters"]["count"] > 0:
                parameters = build_config["parameters"]["property"]
                for parameter in parameters:
                    if parameter["name"] == match.group(0)[1:-1]:
                        value = parameter.get("value", None)
            if not value:
                print(
                    "VALUE NOT FOUND FOR BUILD TYPE " + build_type_id + " AND CONTEXT " + context + ": NO PARAMETER CALLED " + match.group(
                        0))
                print("BUILD TYPE ID" + build_info[
                    "buildTypeId"] + "DISQUALIFIED: GITHUB CONTEXT CONTAINS REFERENCES TO NON-EXISTENT PARAMETERS")
                bad_list.append(build_info["buildTypeId"])
                break
            context = context.replace(match.group(0), value)
            match = re.search(regex_pattern, context)
        if not value:
            continue

        # Extract repo details----------------------------------------------------------------------------------------------
        # Here we extract the owner/repo part of the Github url
        repo_details = None
        vcs_root_entries = build_config["vcs-root-entries"]["vcs-root-entry"]
        for entry in vcs_root_entries:
            repo_details = ""
            try:
                vcs_root = entry["id"]
                url = endpoint + "/app/rest/vcs-roots/id:{id}".format(id=vcs_root)
                response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
                vcs_properties = json.loads(response.text)
                properties = vcs_properties["properties"]["property"]
                for property in properties:
                    if property["name"] == "url":
                        repo_details = "/".join(property["value"].split("/")[-2:]).replace(".git", "").split(":")[-1]
                        break
                if repo_details:
                    break
            except Exception as e:
                print("EXCEPTION: " + str(e))
            if not repo_details:
                print("BUILD TYPE ID" + build_info["buildTypeId"] + "DISQUALIFIED: NO REPO DETAILS")
                bad_list.append(build_info["buildTypeId"])
                continue
        # ------------------------------------------------------------------------------------------------------------------

        # If all necessary information has been found - add the build to the dict
        if repo_details and commit and timestamp:
            try:
                total_info = {"type_id": build_info["buildTypeId"], "repo": repo_details, "commit": commit,
                              "timestamp": timestamp, "status": build_info["status"], "context": context,
                              "build_url": web_url, "state": build["state"]}
                build_info_list.append(total_info)
                print(
                    "COLLECTED INFO: BUILD ID: " + build_type_id + " REPO: " + repo_details + " COMMIT: " + commit + " STATE: " +
                    build["state"] + " TIMESTAMP: " + str(timestamp) + " STATUS: " + build_info.get("status",
                                                                                                    None) + " CONTEXT: " + context)
            except Exception:
                # print("FAILED TO ADD: \n" + str(build_info) + "\n\n")
                pass

    print("\n")
    print("FILTERED OUT {number} OUTDATED BUILDS".format(number=repeats))
    print("DISQUALIFIED {number} BUILD CONFIGS:".format(number=len(bad_list)))
    for config in bad_list:
        print("- " + config)
    print("STATUSES TO FORWARD: " + str(len(build_info_list)))
    print("\n")

    # Post status to GitHub ------------------------------------------------------------------------------------------------

    # Github token
    token = os.environ.get("GH_TOKEN")

    header = {
        'Authorization': 'token ' + str(token),
        'Accept': 'application/vnd.github.polaris-preview'
    }
    url_template = "https://api.github.com/repos/{repo_info}/statuses/{sha}"
    for build in build_info_list:
        url = url_template.format(repo_info=build["repo"], sha=build["commit"])
        data = {"state": "pending",
                "target_url": build["build_url"],
                "context": build["context"],
                "description": "Build pending."
                }
        if build["status"] == "SUCCESS" and build["state"] == "finished":
            data["description"] = "Build succeeded!"
            data["state"] = "success"
        if build["status"] == "FAILURE" and build["state"] == "finished":
            data["description"] = "Build failed."
            data["state"] = "failure"
        if build["state"] == "queued":
            data["description"] = "Build queued."
            data["state"] = "pending"
        if build["state"] == "running":
            data["description"] = "Build running."
            data["state"] = "pending"
        encoded_data = json.dumps(data).encode("utf-8")
        print("POSTING STATUS FOR " + url + "\n- DATA " + str(data))
        response = requests.post(url=url, data=encoded_data, headers=header)
        print("- RESPONSE: " + str(response) + "\n")