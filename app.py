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

# Set up dataframe from CSV to calculate the LDistance
def createDataFrame():
    global df
    df = pd.read_csv("csgbot_data.csv")
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
    token=os.environ.get("xoxb-2046135481284-2036922082501-JMGgPPvSz2WHfs0mvysGa1MR"),
    signing_secret=os.environ.get("dd60242251ad619e6f5475ca1ff90d85")
)

createDataFrame()
createQuestionList()
# TODO: Need to update with the relevant usernames of whoever should have access
csgBotAdmins = ['coshew']
accessDenied = "no no you sneaky moose"

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

# Create a command for fetching the latest version of the CSV used for the questions and responses
@app.command("/csgbot-data")
def repeat_text(ack, say, command):
    if command["user_name"] in csgBotAdmins:
        ack()
        # TODO: Need to update the URL to where the CSV ends up being hosted.
        blocks = [{
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "Click the button to get the latest version of the data CSV."
            },
            "accessory": {
              "type": "button",
              "text": {
                "type": "plain_text",
                "text": "Download CSV"
              },
              "value": "csv_download",
              "url": "https://ecornell.s3.amazonaws.com/casey/sandbox/csgbot_data.csv",
              "action_id": "button-action"
            }
          }]
        say(blocks=blocks)
    else:
        say(accessDenied)

# Create a command for deleting a row of info from the CSV
@app.command("/csgbot-remove")
def open_modal(ack, body, client, command, say):
    if command["user_name"] in csgBotAdmins:
        ack()
        client.views_open(
            # Pass a valid trigger_id within 3 seconds of receiving it
            trigger_id=body["trigger_id"],
            # View payload
            view={
            	"title": {
            		"type": "plain_text",
            		"text": "Remove CSGBot Data"
            	},
            	"submit": {
            		"type": "plain_text",
            		"text": "Submit"
            	},
            	"blocks": [
            		{
            			"type": "section",
            			"text": {
            				"type": "plain_text",
            				"text": "Specify the row number of the row you'd like to remove from the CSV."
            			}
            		},
            		{
            			"type": "input",
            			"block_id": "removeRowID",
            			"element": {
            				"type": "plain_text_input",
            				"action_id": "removeRowAction"
            			},
            			"label": {
            				"type": "plain_text",
            				"text": "Question"
            			}
            		}
            	],
            	"type": "modal",
                "callback_id": "removeRowSubmit",
            }
        )
    else:
        say(accessDenied)

# Remove the specified row from the dataframe and resave the CSV
@app.view("removeRowSubmit")
def handle_submission(ack, body, client, view, logger, say):
    ack()
    global df
    removeRowString = view["state"]["values"]["removeRowID"]["removeRowAction"]["value"]
    removeRowIndex = int(removeRowString) - 2
    df = df.drop(removeRowIndex)
    df.to_csv('csgbot_data.csv', index=False)
    createDataFrame()
    createQuestionList()


# Create a command for adding rows of info to the CSV
@app.command("/csgbot-upload")
def open_modal(ack, body, client, command, say):
    if command["user_name"] in csgBotAdmins:
        ack()
        client.views_open(
            # Pass a valid trigger_id within 3 seconds of receiving it
            trigger_id=body["trigger_id"],
            # View payload
            view={
            	"title": {
            		"type": "plain_text",
            		"text": "Add CSGBot Data"
            	},
            	"submit": {
            		"type": "plain_text",
            		"text": "Submit"
            	},
            	"blocks": [
            		{
            			"type": "section",
            			"text": {
            				"type": "plain_text",
            				"text": "Populate every field to add a new question and response to CSGBot's repertoire."
            			}
            		},
            		{
            			"type": "input",
            			"block_id": "newQuestionID",
            			"element": {
            				"type": "plain_text_input",
            				"action_id": "newQuestionAction"
            			},
            			"label": {
            				"type": "plain_text",
            				"text": "Question"
            			}
            		},
            		{
            			"type": "input",
            			"block_id": "newKeywordsID",
            			"element": {
            				"type": "plain_text_input",
            				"action_id": "newKeywordsAction"
            			},
            			"label": {
            				"type": "plain_text",
            				"text": "Keywords"
            			}
            		},
            		{
            			"type": "input",
            			"block_id": "newResponseID",
            			"element": {
            				"type": "plain_text_input",
            				"action_id": "newResponseAction"
            			},
            			"label": {
            				"type": "plain_text",
            				"text": "Response"
            			}
            		}
            	],
            	"type": "modal",
                "callback_id": "newRowSubmit",
            }
        )
    else:
        say(accessDenied)

# When a new question is submitted, add it to the dataframe and then save that to CSV again
@app.view("newRowSubmit")
def handle_submission(ack, body, client, view, logger, say):
    ack()
    newQuestion = view["state"]["values"]["newQuestionID"]["newQuestionAction"]["value"]
    newKeyWords = view["state"]["values"]["newKeywordsID"]["newKeywordsAction"]["value"]
    newResponse = view["state"]["values"]["newResponseID"]["newResponseAction"]["value"]
    newSearch = newQuestion + " " + newKeyWords

    global df

    blankRowBool = df.iloc[:,1].isna()
    blankRowIndex =  [i for i, x in enumerate(blankRowBool) if x][0]

    df.loc[blankRowIndex] = [newQuestion, newKeyWords, newResponse, "", newSearch,]

    df.to_csv('csgbot_data.csv', index=False)
    createDataFrame()
    createQuestionList()


# Handle non-CSGBot messages
@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

# Start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 5000)))
