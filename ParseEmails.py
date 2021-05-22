from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
import re
import parseprice


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
    body_list  = []

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
    result = service.users().messages().list(userId='me', maxResults=num,labelIds = ['INBOX']).execute()

    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')

    # messages is a list of dictionaries where each dictionary contains a message id.

    # iterate through all the messages
    for i,msg in enumerate(messages):
        # Get the message from its id
        info = []
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
            body_list= body.split("\n")
        #    service.users().messages().modify(userId='me', id=msg['id'], body = {'removeLabelIds': ['UNREAD']}).execute()


        except:
            continue
        info.append((sender, subject, body_list))
    return info


def is_git_freight_quote_subject(subject):
  re2 = "#[0-9]{10}-[0-9]{3}"
  a = re.findall(re2, subject)
  if len(a) == 0:
    return False
  else:
    return True

def get_major_minor_ids(subject):
  ID1 = subject.split("#")
  major_ID = ID1[1]
  major_ID1 = major_ID.split("-")
  ID2 = major_ID.split("-")
  minor_ID = ID2[1]
  # subject.split("#")
  # split("-")

  return [major_ID1[0], minor_ID]

emails = getEmails(1)
print(emails)
for a in emails:
    subject = a[1]
    print ("subject:",subject)
    print(is_git_freight_quote_subject(subject))
    if is_git_freight_quote_subject(subject):
        result = {}
        b = parseprice.extractPrice(a[2])
        # print ("Test", b)
        for h in b:
            if 'rate' in h["DETAIL"].lower() or 'line haul' in h["DETAIL"].lower() or 'shipment' in h['DETAIL'].lower():
                result = h
        result['Major_ID'] = get_major_minor_ids(subject)[0]
        result['Minor_ID'] = get_major_minor_ids(subject)[1]
        print(result)

