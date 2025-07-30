import requests
import json

def send_teams_workflow_webhook(
    webhook_url,
    main_title="",
    main_msg="",
):
    headers = { "Content-Type": "application/json" }
    message_to_send = {
        "subject": main_title,
        "messageContent": main_msg,
    }
    print(json.dumps(message_to_send))
    response = requests.post(webhook_url, data=json.dumps(message_to_send), headers=headers)

    print(f"Send Webhook Result : {response.status_code}, {response.text}")

    return response.status_code
