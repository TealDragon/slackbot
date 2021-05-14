import ssl
import os
import re
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App

ssl._create_default_https_context = ssl._create_unverified_context
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Set up dataframe from CSV to calculate the LDistance
df = pd.read_csv("csgbot_data.csv")
df["search"] = df["Question"] + " " + df["Keywords"]

# Set up string with possible questions
question_col = df["Question"]
question_list = ""
for question in question_col:
    if isinstance(question, str):
        question_list = question_list + question + '\n'

# Initializes the app with bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Listen to incoming messages containing CSGBot and respond
@app.message(re.compile("(CSGBot|csgbot|csg bot|CSG Bot)"))
def message_hello(message, say):
    question = message["text"].replace("CSGBot", "")
    match = process.extractOne(question, df["search"], scorer=fuzz.token_set_ratio)
    response = df.iloc[match[2], 2]
    if match[1] >= 50:
        say(
            blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response}
            }
        ],
        text=response
    )
        print(match[1])
    else:
        say(
            blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "I'm sorry, I can't find an answer to that. Click the button to see a list of questions I can answer."},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Question List"},
                    "action_id": "button_click"
                }
            }
        ],
        text="I'm sorry, I can't find an answer to that. Click the button to see a list of questions I can answer."
    )
        print(match[1])

# Show question list if the button is clicked

@app.action("button_click")
def action_button_click(body, ack, say):
    ack()
    say(question_list)


# Handle non-CSGBot messages
@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

# Start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 5000)))
