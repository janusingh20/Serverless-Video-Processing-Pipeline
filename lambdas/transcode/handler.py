def lambda_handler(event, context):
    key = event.get("key","")
    event["videoId"] = key.split("/",1)[0] if "/" in key else key
    return event
