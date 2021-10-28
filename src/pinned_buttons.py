
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

