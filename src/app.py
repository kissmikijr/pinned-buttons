import os
from collections import defaultdict

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

magnet_threads = defaultdict(list)
pinned_message_ts = None

@app.message("magnet")
def message_hello(message, say):
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
    magnet_threads[message.get("ts")].append(result.get("ts"))

@app.event({
    "type": "message",
    "subtype": "message_changed"
})
def delete_response(message, say, event, client):
    channel = message.get("channel")
    message = message.get("message",{})
    if message.get("subtype", "") == "tombstone":
        ts = message.get("ts")
        if is_magnet_thread(ts):
            replies = magnet_threads[ts]
            for r_ts in replies:
                client.chat_delete(channel=channel, ts=r_ts)
                print(f"deleted message {message.get('text')}")

def is_magnet_thread(ts):
    if ts in magnet_threads:
        return True 
    return False


blocks = [
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "google",
                    "emoji": True
                },
                "value": "click_me_123",
                "url": "https://google.com"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Troubleshoot Guide",
                    "emoji": True
                },
                "value": "click_me_123",
                "url": "https://prezidoc.com"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "How To Ask",
                    "emoji":True
                },
                "value": "click_me_123",
                "url": "https://prezidoc.com"
            }
        ]
    }

]

@app.event("channel_joined")
def post_initial_message(say):
    global pinned_message_ts

    result = say(blocks=blocks)
    pinned_message_ts = result["ts"]

@app.message(r'.*')
def pinned_buttons(client, say,  message):
    global pinned_message_ts


    if not pinned_message_ts:
        result = say(blocks=blocks)
        pinned_message_ts = result["ts"]
    else:
        if float(message["ts"]) > float(pinned_message_ts):
            client.chat_delete(channel=message["channel"], ts=pinned_message_ts)
            result = say(blocks=blocks)
            pinned_message_ts = result["ts"]

@app.command("/pinned")
def pinned_buttons_editor(ack, client, body):
    ack()

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "pinned_buttons_editor",
            "title": {"type": "plain_text", "text":"Pinned Buttons Editor"},
             "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "input_a",
                    "label": {"type": "plain_text", "text": "Banner"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "banner",
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_b",
                    "label": {"type": "plain_text", "text": "Buton 1"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "banner",
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_c",
                    "label": {"type": "plain_text", "text": "Buton 1 Link"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "banner",
                    }
                }
            ]
        }
    )


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
