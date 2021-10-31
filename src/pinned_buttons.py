import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from db import get_database

dbname = get_database()
pinned_buttons_channel_data = dbname["pinned_buttons_channel_data"]

load_dotenv()

app = App(token=os.environ.get("PINNED_BUTTONS_SLACK_BOT_TOKEN"))

def get_pinned_buttons_schema(banner, button_1, button_1_link, button_2, button_2_link, button_3, button_3_link):
	return [{
            "type": "section",   
            "text": {
                "type": "mrkdwn",
                "text": banner
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": button_1,
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "url": button_1_link
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": button_2,
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "url": button_2_link
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": button_3,
                        "emoji":True
                    },
                    "value": "click_me_123",
                    "url": button_3_link
                }
            ]
        }]

@app.event("message")
def pinned_buttons(ack, client, say,  message, body):
    ack()

    if message.get("subtype"):
        return

    channel_data = list(pinned_buttons_channel_data.find({"channel_id": message["channel"]}))
    if not channel_data:
        return

    blocks = get_pinned_buttons_schema(
        banner=channel_data[0]["pinned_buttons"]["banner"],
        button_1=channel_data[0]["pinned_buttons"]["button_1"],
        button_1_link=channel_data[0]["pinned_buttons"]["button_1_link"],
        button_2=channel_data[0]["pinned_buttons"]["button_2"],
        button_2_link=channel_data[0]["pinned_buttons"]["button_2_link"],
        button_3=channel_data[0]["pinned_buttons"]["button_3"],
        button_3_link=channel_data[0]["pinned_buttons"]["button_3_link"]
    )

    pinned_message_ts = channel_data[0].get("pinned_message_ts", None)

    if not pinned_message_ts:
        result = say(blocks=blocks)
    else:
        client.chat_delete(channel=message["channel"], ts=pinned_message_ts)
        result = say(blocks=blocks)

    pinned_buttons_channel_data.update_one({"channel_id": message["channel"]}, {'$set': {"pinned_message_ts": result["ts"]}})

@app.command("/pinned")
def pinned_buttons_editor(ack, client, body ):

    ack()

    channel_datas = list(pinned_buttons_channel_data.find({"channel_id": body["channel_id"]}))

    channel_data = {}
    if channel_datas:
        channel_data = channel_datas[0]

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "pinned_buttons_editor",
            "title": {"type": "plain_text", "text":"Pinned Buttons Editor"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": body["channel_id"],
            "blocks": [
                {
                    "type": "input",
                    "block_id": "banner",
                    "label": {"type": "plain_text", "text": "Banner"},
                    "element": {
                        "type": "plain_text_input",
                        "initial_value": channel_data.get("pinned_buttons", {}).get("banner", ""),
                        "action_id": "banner_action"
                    }
                },
                {"type": "divider"},
                {
                    "type": "input",
                    "block_id": "button_1",
                    "label": {"type": "plain_text", "text": "Buton 1"},
                    "element": {
                        "type": "plain_text_input",
                        "initial_value": channel_data.get("pinned_buttons", {}).get("button_1", ""),
                        "action_id": "button_1_action"
                    }
                },
                {
                    "type": "input",
                    "block_id": "button_1_link",
                    "label": {"type": "plain_text", "text": "Buton 1 Link"},
                    "element": {
                        "type": "plain_text_input",
                        "initial_value": channel_data.get("pinned_buttons", {}).get("button_1_link", ""),
                        "action_id": "button_1_link_action"
                    }
                },
                {"type": "divider"},
                {
                    "type": "input",
                    "block_id": "button_2",
                    "label": {"type": "plain_text", "text": "Buton 2"},
                    "element": {
                        "type": "plain_text_input",
                        "initial_value": channel_data.get("pinned_buttons", {}).get("button_2", ""),
                        "action_id": "button_2_action"
                    }
                },
                {
                    "type": "input",
                    "block_id": "button_2_link",
                    "label": {"type": "plain_text", "text": "Buton 2 Link"},
                    "element": {
                        "type": "plain_text_input",
                        "initial_value": channel_data.get("pinned_buttons", {}).get("button_2_link", ""),
                        "action_id": "button_2_link_action"
                    }
                },
                {"type": "divider"},
                {

                    "type": "input",
                    "block_id": "button_3",
                    "label": {"type": "plain_text", "text": "Buton 3"},
                    "element": {
                        "type": "plain_text_input",
                        "initial_value": channel_data.get("pinned_buttons", {}).get("button_3", ""),
                        "action_id": "button_3_action"
                    }
                },
                {
                    "type": "input",
                    "block_id": "button_3_link",
                    "label": {"type": "plain_text", "text": "Buton 3 Link"},
                    "element": {
                        "type": "plain_text_input",
                        "initial_value": channel_data.get("pinned_buttons", {}).get("button_3_link", ""),
                        "action_id": "button_3_link_action"
                    }
                },


            ]
        }
    )
@app.view("pinned_buttons_editor")
def handle_view_events(ack, body, client):
    ack()

    result = pinned_buttons_channel_data.update_one({"channel_id":body["view"]["private_metadata"]},{"$set":{
        "channel_id": body["view"]["private_metadata"],
        "pinned_buttons": {
            "banner": body["view"]["state"]["values"]["banner"]["banner_action"]["value"],

            "button_1": body["view"]["state"]["values"]["button_1"]["button_1_action"]["value"],
            "button_1_link": body["view"]["state"]["values"]["button_1_link"]["button_1_link_action"]["value"],

            "button_2": body["view"]["state"]["values"]["button_2"]["button_2_action"]["value"],
            "button_2_link": body["view"]["state"]["values"]["button_2_link"]["button_2_link_action"]["value"],

            "button_3": body["view"]["state"]["values"]["button_3"]["button_3_action"]["value"],
            "button_3_link": body["view"]["state"]["values"]["button_3_link"]["button_3_link_action"]["value"]
        }}
    },upsert=True)

    blocks = get_pinned_buttons_schema(
        banner=body["view"]["state"]["values"]["banner"]["banner_action"]["value"],

        button_1=body["view"]["state"]["values"]["button_1"]["button_1_action"]["value"],
        button_1_link=body["view"]["state"]["values"]["button_1_link"]["button_1_link_action"]["value"],

        button_2=body["view"]["state"]["values"]["button_2"]["button_2_action"]["value"],
        button_2_link=body["view"]["state"]["values"]["button_2_link"]["button_2_link_action"]["value"],

        button_3=body["view"]["state"]["values"]["button_3"]["button_3_action"]["value"],
        button_3_link=body["view"]["state"]["values"]["button_3_link"]["button_3_link_action"]["value"],
    )

    channel_data = list(pinned_buttons_channel_data.find({"channel_id": body["view"]["private_metadata"]}))[0]
    if channel_data.get("pinned_message_ts"):
        client.chat_delete(channel=body["view"]["private_metadata"], ts=channel_data.get("pinned_message_ts"))

    result = client.chat_postMessage(channel=body["view"]["private_metadata"], blocks=blocks)
    pinned_buttons_channel_data.update_one({"channel_id":body["view"]["private_metadata"] },{"$set": {"pinned_message_ts": result["ts"]}})


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["PINNED_BUTTONS_SLACK_APP_TOKEN"]).start()

