import ssl
import slack
import os
from pathlib  import Path
from dotenv import load_dotenv

ssl._create_default_https_context = ssl._create_unverified_context

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

client.chat_postMessage(channel='#csgbot', text="I am become csgbot, destroyer of worlds")
