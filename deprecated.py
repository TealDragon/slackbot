# Deprecated functionality below this line

#csgBotAdmins = ['coshew']
#accessDenied = "no no you sneaky moose"

# No longer needed with content hosted on google sheets
# Create a command for fetching the latest version of the CSV used for the questions and responses
#@app.command("/csgbot-data")
#def repeat_text(ack, say, command):
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

# No longer needed with content hosted on google sheets
# Create a command for deleting a row of info from the CSV
#@app.command("/csgbot-remove")
#def open_modal(ack, body, client, command, say):
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

# No longer needed with content hosted on google sheets
# Remove the specified row from the dataframe and resave the CSV
#@app.view("removeRowSubmit")
#def handle_submission(ack, body, client, view, logger, say):
    ack()
    global df
    removeRowString = view["state"]["values"]["removeRowID"]["removeRowAction"]["value"]
    removeRowIndex = int(removeRowString) - 2
    df = df.drop(removeRowIndex)
    df.to_csv('csgbot_data.csv', index=False)
    createDataFrame()
    createQuestionList()

# No longer needed with content hosted on google sheets
# Create a command for adding rows of info to the CSV
#@app.command("/csgbot-upload")
#def open_modal(ack, body, client, command, say):
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

# No longer needed with content hosted on google sheets
# When a new question is submitted, add it to the dataframe and then save that to CSV again
#@app.view("newRowSubmit")
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
