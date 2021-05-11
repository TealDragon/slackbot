import ssl
import os
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App

ssl._create_default_https_context = ssl._create_unverified_context
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


# Initializes the app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Listens to incoming messages that contain "hello"
@app.message("frame.io")
def message_hello(message, say):
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Oh I got the goods on frame.io"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Not what you were looking for? See list of questions."},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Oh I got the goods on frame.io"
    )

# Responds to button click
@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")

# Start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 5000)))
