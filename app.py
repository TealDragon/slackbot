import ssl
import os
import re
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App

# Set the environment variable path and resolve SSL error
ssl._create_default_https_context = ssl._create_unverified_context
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Grab the CSV location from google drive
url = 'https://drive.google.com/file/d/1-lCFfce0O_uhiAsR7GqNYqSAt6aR1IKO/view?usp=sharing'
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]

# Set up dataframe from CSV to calculate the LDistance
def createDataFrame():
    global df
    df = pd.read_csv(path)
    df["search"] = df["Question"] + " " + df["Keywords"]

# Set up string with possible questions
def createQuestionList():
    global questionList
    questionCol = df["Question"]
    questionList = ""
    for question in questionCol:
        if isinstance(question, str):
            questionList = questionList + ' - ' + question + '\n'

# Initializes the app with bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

createDataFrame()
createQuestionList()

# Listen to incoming messages
@app.message(" ")
def message_hello(message, say):
    messageText = message["text"]
    match = process.extractOne(messageText, df["search"], scorer=fuzz.token_set_ratio)
    response = df.iloc[match[2], 2]
    # If there is a response with a LDistance of 60 or greater, return the best response from the CSV
    if match[1] >= 60:
        say(
            blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": response}
            }
        ],
        text=response
    )
    # If there is no reponse with an LDistance of 60 or greater, tell the user CSGBot has no answer, offer the list of questions it can answer, and ping a private channel with the unanswered question
    else:
        global noMatchReply
        noMatchReply = say(
            blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "I'm sorry, I can't find an answer to that. Click the button to see a thread containing the list of questions I can answer."},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "See Question List"},
                    "action_id": "button_click"
                }
            }
        ],
        text="I'm sorry, I can't find an answer to that. Click the button to see a thread containing the list of questions I can answer."
    )
        noMatchReply
        # TODO: this channel ID needs to be changed based on where we want alerts coming through
        say(text=f"The user <@{message['user']}> sent the unanswered question: " + messageText, channel="C022GLE1Q5B")


# Show question list if the button is clicked
@app.action("button_click")
def action_button_click(body, ack, say):
    ack()
    say(text=questionList, thread_ts=(noMatchReply["ts"]))
    print(noMatchReply["ts"])


# Refresh the dataframe based on updated info
@app.command("/csgbot-refresh")
def refresh_data ():
    createDataFrame()
    createQuestionList()


# Handle non-CSGBot messages
@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

# Start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 5000)))
