import os
from collections import defaultdict

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from db import get_database
from pinned_buttons import get_pinned_buttons_schema

dbname = get_database()
channel_collection = dbname["channel_data"]
magnet_collection = dbname["magnet_threads"]

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message("magnet")
def magnet_reply(message, say):
    blocks = [
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": "Dear Magnet pls take a looka at this:"
					}
				},
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": message["text"]
					}
				}
			]
    result = say({"thread_ts":message.get("ts"), "blocks": blocks})

    magnet_collection.insert_one({"magnet_request_ts": message.get("ts"), "magnet_reply_ts": result["ts"]})

@app.event({
    "type": "message",
    "subtype": "message_changed"
})
def delete_response(message, say, event, client):
    channel = message.get("channel")
    message = message.get("message",{})
    if message.get("subtype", "") == "tombstone":
        ts = message.get("ts")

        magnet_request_cursor = magnet_collection.find({"magnet_request_ts": ts})

        if magnet_request_cursor.count() == 0:
            return

        for magnet_request in magnet_request_cursor:
            client.chat_delete(channel=channel, ts=magnet_request["magnet_reply_ts"])

        magnet_collection.delete_many(magnet_request_cursor)


@app.message(r'.*')
def pinned_buttons(client, say,  message):
    channel_data = list(channel_collection.find({"channel_id": message["channel"]}))
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

    channel_collection.update_one({"channel_id": message["channel"]}, {'$set': {"pinned_message_ts": result["ts"]}})

@app.command("/magneto")
def magneto_settings(ack,client, body):
    ack()

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Magneto",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Magnet: miklos.kiss"
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Magnet Override",
                            "emoji": True
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "magnet_1",
                                    "emoji": True
                                },
                                "value": "value-0"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "magnet_2",
                                    "emoji": True
                                },
                                "value": "value-1"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "magnet_3",
                                    "emoji": True
                                },
                                "value": "value-2"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "None",
                                    "emoji": True
                                },
                                "value": "value-3"
                            }
                        ],
                        "action_id": "static_select-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Magnet Override",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "PagerDuty Schedule",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "plain_text_input-action",
                        "initial_value": "#label_1 #label_2 #label_1 #label_2 #label_1 #label_2 #label_1 #label_2 #label_1 #label_2 #label_1 #label_2 #label_1 #label_2 "
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Labels",
                        "emoji": True
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "plain_text_input-action",
                        "initial_value": "{{magnet}}:{{message}}"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Template",
                        "emoji": True
                    }
                }
            ]
        }
    )


@app.command("/pinned")
def pinned_buttons_editor(ack, client, body ):

    ack()

    channel_datas = list(channel_collection.find({"channel_id": body["channel_id"]}))

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

    result = channel_collection.update_one({"channel_id":body["view"]["private_metadata"]},{"$set":{
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

    channel_data = list(channel_collection.find({"channel_id": body["view"]["private_metadata"]}))[0]
    if channel_data.get("pinned_message_ts"):
        client.chat_delete(channel=body["view"]["private_metadata"], ts=channel_data.get("pinned_message_ts"))

    result = client.chat_postMessage(channel=body["view"]["private_metadata"], blocks=blocks)
    channel_collection.update_one({"channel_id":body["view"]["private_metadata"] },{"$set": {"pinned_message_ts": result["ts"]}})


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
