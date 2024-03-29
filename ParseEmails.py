from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
import re
import parseprice
import time


def remove(body):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    body = body.replace('\n', " ")
    body = body.replace('-', "")
    body = re.sub(regex, '', body)
    body = re.sub(r'http\S+', '', body)

    return body


def getEmails(num=1):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    body = ''
    body_list = []
    f = open("timestamp.txt", "r")
    previous_timestamp = f.read()
    f.close()
    timestamp = str(round(time.time()))
    f = open("timestamp.txt", "w")
    f.write(timestamp)
    f.close()
    # The file token.pickle contains the user access token.
    # Check if it exists
    if os.path.exists('token.pickle'):
        # Read the token from the file and store it in the variable creds
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

            # If credentials are not available or are invalid, ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

            # Save the access token in token.pickle file for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

            # Connect to the Gmail API
    service = build('gmail', 'v1', credentials=creds)

    # request a list of all the messages
    result = service.users().messages().list(userId='me',  q="in: after:" + previous_timestamp,labelIds = ['INBOX']).execute()

    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')

    # messages is a list of dictionaries where each dictionary contains a message id.

    # iterate through all the messages
    info = []
    if messages != None:

        for i, msg in enumerate(messages):
            # Get the message from its id

            txt = service.users().messages().get(userId='me', id=msg['id'], format="full").execute()
            print(txt)
            # Use try-except to avoid any Errors
            try:
                # Get value of 'payload' from dictionary 'txt'
                payload = txt['payload']
                headers = payload['headers']

                # Look for Subject and Sender Email in the headers
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']

                # The Body of the message is in Encrypted format. So, we have to decode it.
                # Get the data and decode it with base 64 decoder.
                parts = payload.get('parts')[0]
                data = parts['body']['data']
                data = data.replace("-", "+").replace("_", "/")

                # Now, the data obtained is in lxml. So, we will parse
                # it with BeautifulSoup library

                msg = base64.urlsafe_b64decode(data.encode('UTF8'))
                body = str(email.message_from_bytes(msg))
                # print(email.message_from_bytes(msg))
                body_list = body.split("\n")
                print(body)
                body_list = list(filter(None, body_list))
            #    service.users().messages().modify(userId='me', id=msg['id'], body = {'removeLabelIds': ['UNREAD']}).execute()

            except Exception as e:
                print(e)
                continue
            info.append((sender, subject, body_list))
    return info


def is_git_freight_quote_subject(subject):
    re2 = "#[0-9]{10}-[0-9]{3}-[0-9]{3}"
    a = re.findall(re2, subject)
    if len(a) == 0:
        return False
    else:
        return True


def get_major_minor_user_ids(subject):
    ID1 = subject.split("#")
    major_ID = ID1[1]
    major_ID1 = major_ID.split("-")
    ID2 = major_ID.split("-")
    minor_ID = ID2[1]
    userID = ID2[2]
    # subject.split("#")
    # split("-")

    return [major_ID1[0], minor_ID, userID]

# TODO
# 1. getEmails bug fix
# 2. migrate the repl server back to this project: https://replit.com/join/fhcmpzms-sunyu912
# 3. write the quote results back to the DB
# 4. periodic runner with timestamp to keep loading the emails
# 5. update the API to get the quote data with best pricing algorithm
