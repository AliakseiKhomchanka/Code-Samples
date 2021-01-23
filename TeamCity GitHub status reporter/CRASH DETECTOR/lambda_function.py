import requests
import os
import json
from datetime import datetime, timedelta
import copy
import boto3


client = boto3.client('lambda')
s3 = boto3.resource('s3')
sns_client = boto3.client('sns')


def lambda_handler(event, context):
    username, password = os.environ.get("TC_USERNAME"), os.environ.get("TC_PASSWORD")
    status = "HEALTHY"
    build_interval = int(os.environ.get("BUILD_INTERVAL"))
    check_age = build_interval + 2
    headers = {'Content-Type': 'application/xml',
               'Accept': 'application/json'}

    endpoint = os.environ.get("TC_ENDPOINT")
    tc_web = os.environ.get("TC_URL")

    function_arn = os.environ.get("FUNCTION_ARN")
    sns_arn = os.environ.get("SNS_ARN")
    
    repo = os.environ.get("REPO")
    ref = os.environ.get("REF")
    
    # Github part
    token = os.environ.get("GH_TOKEN")
    api_call_url = "https://api.github.com/repos/{repo}/commits/{ref}/statuses".format(ref=ref)
    headers = {
        'Authorization': 'token ' + str(token),
        'Accept': 'application/vnd.github.polaris-preview'
    }
    response = requests.get(url=api_call_url, headers=headers)
    response_json = json.loads(response.text)
    
    context = "a2-test-status-update"
    status_checks = [check for check in response_json if check["context"] == context]
    if len(status_checks) == 0:
        status = "BROKEN"
    if status != "BROKEN":
        check_in_question = status_checks[0]
    
    # Timestamps
    interval_mins = build_interval + 30
    now = datetime.utcnow()
    now_timestamp = now
    readable_now = now.strftime("%d-%m-%Y_%H-%M-%S")
    message_now = now.strftime("%d.%m.%Y %H:%M:%S")
    earliest_build_timestamp = now - timedelta(minutes=interval_mins)
    earliest_build_timestamp = earliest_build_timestamp.strftime("'%Y%m%dT%H%M%S'")
    now = now.strftime("'%Y%m%dT%H%M%S'")
    
    if status != "BROKEN":
        # Process statuses and see if the one in question is too old
        update_date = check_in_question["updated_at"]
        print("STATUS CHECK UPDATED AT: " + update_date)
        update_timestamp = datetime.strptime(update_date, '%Y-%m-%dT%H:%M:%SZ')
        if now_timestamp - update_timestamp >= timedelta(minutes=check_age):
            status = "BROKEN"
        print("STATUS: " + status)
    
    # TC fetching
    headers = {'Content-Type': 'application/xml',
               'Accept': 'application/json'}
    
    # Fetch queued builds
    url = endpoint + "/httpAuth/app/rest/builds/?locator=state:queued,branch:default:any,queuedDate:(date:{timestamp},condition:after)".format(
        timestamp=earliest_build_timestamp).replace("\'", "")
    response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
    print(response.text)
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
    
    summary = "Build summary in last {time} minutes:\n".format(time=interval_mins)
    summary += "Queued builds:\n"
    for build in queued_builds:
        entry = build["buildTypeId"] + ":" + "\n- ID: " + str(build["id"]) + "\n- URL: " + build["webUrl"] + "\n"
        summary += entry
    summary += "Running builds:\n"
    for build in running_builds:
        entry = build["buildTypeId"] + ":" + "\n- ID: " + str(build["id"]) + "\n- URL: " + build["webUrl"] + "\n"
        summary += entry
    summary += "Finished builds:\n"
    for build in finished_builds:
        entry = build["buildTypeId"] + ":" + "\n- ID: " + str(build["id"]) + "\n- URL: " + build["webUrl"] + "\n"
        summary += entry
        
    print(summary)
    
    if status == "BROKEN":
        print("STATUS FORWARDING BROKEN")
        print("NO STATUS FOUND FOR REF {ref}".format(ref=ref))
        if os.environ.get("TC_STATUS", None) == "HEALTHY":
            
            env = client.get_function_configuration(FunctionName="OVERSEER-TEAMCITY-STATUS-FORWARDING-CRASH-DETECTOR")["Environment"]
            print("LAMBDA ENV: " + str(env))
            env["Variables"]["TC_STATUS"] = "BROKEN"
            print("NEW ENV: " + str(env))
            response = client.update_function_configuration(FunctionName="OVERSEER-TEAMCITY-STATUS-FORWARDING-CRASH-DETECTOR", 
                                                            Environment=env)
            print(response)
            # Create a summary file
            message = "NOW IS " + message_now + " UTC\n" + "TEAMCITY:\nGithub status forwarding is now BROKEN\n"
            message += "The list of builds in last 30 minutes can be found in this S3 bucket:\nLINK_REDACTED\n"
            message += "TC server logs can be found in this bucket:\nLINK_REDACTED \nAll buckets are in the Devprod account"
            print(message)
            filename = "summary-" + readable_now +"-from-healthy-to-broken.txt" 
            with open("/tmp/" + filename, "w") as file:
                file.write(summary)
            response = s3.meta.client.upload_file('/tmp/' + filename, 'teamcity-status-forwarding-health-reports', filename)
            print(response)
            response = sns_client.publish(TopicArn=sns_arn,
                                          Message=message,
                                          Subject='TeamCity status forwarding BROKEN')
            print(response)
            # Fetch server logs
            logs_list = []
            file_location = tc_web + "/get/file/serverLogs/teamcity-server.log".format(username=username, password=password)
            response = requests.get(file_location, headers=headers, auth=(username, password), timeout=10)
            with open("/tmp/server_log.txt", "w") as file:
                file.write(str(response.content))
                logs_list.append("/tmp/server_log.txt")
            for counter in range(1,20):
                url = file_location + "." + str(counter)
                response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
                with open("/tmp/server_log_" + str(counter) + ".txt", "w") as file:
                    file.write(str(response.content))
                    logs_list.append("/tmp/server_log_" + str(counter) + ".txt")
            for file in logs_list:
                response = s3.meta.client.upload_file(file, 'teamcity-fetched-server-logs', readable_now + "/" + file)
                print(response)
            
    else:
        print("STATUS FORWARDING WORKS")
        print("PROPER STATUS FOUND FOR REF {ref}".format(ref=ref))
        print(str(status_checks[0]))
        if os.environ.get("TC_STATUS", None) == "BROKEN":
            env = client.get_function_configuration(FunctionName="OVERSEER-TEAMCITY-STATUS-FORWARDING-CRASH-DETECTOR")["Environment"]
            print("LAMBDA ENV: " + str(env))
            env["Variables"]["TC_STATUS"] = "HEALTHY"
            print("NEW ENV: " + str(env))
            response = client.update_function_configuration(FunctionName="OVERSEER-TEAMCITY-STATUS-FORWARDING-CRASH-DETECTOR", 
                                                 Environment=env)
            print(response)
            # Create a summary file
            message = "NOW IS " + message_now + " UTC\n" + "TEAMCITY:\nGithub status forwarding is now HEALTHY\nPlease retrieve the teamcity-server.log manually\n"
            message += "The list of builds in last 30 minutes can be found in this S3 bucket:\nhttps://s3.console.aws.amazon.com/s3/buckets/teamcity-status-forwarding-health-reports/?region=us-west-2&tab=overview\n"
            message += "TC server logs can be found in this bucket:\nhttps://s3.console.aws.amazon.com/s3/buckets/teamcity-fetched-server-logs/?region=us-west-2&tab=overview \nAll buckets are in the Devprod account"
            print(message)
            filename = "summary-" + readable_now +"-from-broken-to-healthy.txt"
            with open("/tmp/" + filename, "w") as file:
                file.write(summary)
            response = s3.meta.client.upload_file('/tmp/' + filename, 'teamcity-status-forwarding-health-reports', filename)
            print(response)
            response = sns_client.publish(TopicArn=sns_arn,
                                          Message=message,
                                          Subject='TeamCity status forwarding HEALTHY')
            print(response)
            # Fetch server logs
            logs_list = []
            file_location = tc_web + "/get/file/serverLogs/teamcity-server.log".format(username=username, password=password)
            response = requests.get(file_location, headers=headers, auth=(username, password), timeout=10)
            with open("/tmp/server_log.txt", "w") as file:
                file.write(str(response.content))
                logs_list.append("/tmp/server_log.txt")
            for counter in range(1,20):
                url = file_location + "." + str(counter)
                response = requests.get(url, headers=headers, auth=(username, password), timeout=10)
                with open("/tmp/server_log_" + str(counter) + ".txt", "w") as file:
                    file.write(str(response.content))
                    logs_list.append("/tmp/server_log_" + str(counter) + ".txt")
            for file in logs_list:
                response = s3.meta.client.upload_file(file, 'teamcity-fetched-server-logs', readable_now + "/" + file)
                print(response)
