import pandas as pd
from fuzzywuzzy import process

question = input("What is your question for csgBot?")

# Convert CSV to pandas dataframe
df = pd.read_csv("csgbot_data.csv")

# Create column combining keywords and questions for calculating the Ldistance
df["search"] = df["Question"] + " " + df["Keywords"]
df["LDistance"] = ""

# Find the row with the closest match to the question
match = process.extractOne(question, df["search"])
response = df.iloc[match[2], 2]

if match[1] < 50:
    print("I'm sorry, I don't have an answer. Please see list of questions.")

else:
    print(response)
    print(match)
