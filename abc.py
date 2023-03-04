from flask import Flask, jsonify
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

app = Flask(__name__)

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Function to get Gmail service
def get_gmail_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', scopes=SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    return service

# Function to get email body from the message ID
def get_email_data(service, user_id, msg_id):
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    payload = message['payload']
    if 'parts' in payload:
        parts = payload['parts']
    else:
        parts = [payload]
    data = ''
    for part in parts:
        if part['body'].get('attachmentId'):
            attachment = service.users().messages().attachments().get(
                userId=user_id, messageId=msg_id, id=part['body']['attachmentId']
            ).execute()
            data += base64.urlsafe_b64decode(
                attachment['data'].encode('UTF-8')
            ).decode('UTF-8')
        else:
            part_data = part['body']['data']
            cleaned_part_data = part_data.replace("-","+").replace("_","/")
            data += base64.urlsafe_b64decode(
                cleaned_part_data.encode('UTF-8')
            ).decode('UTF-8')
    soup = BeautifulSoup(data, 'html.parser')
    date = message['internalDate']
    body_text = soup.get_text().replace('\\', '').replace(' ', '')
    return {'subject': message['snippet'], 'body': body_text, 'date': date}


@app.route('/emails', methods=['GET'])
def get_emails():
    # Get the Gmail service
    service = get_gmail_service()

    # Get the latest 5 messages from the inbox and get their email data
    messages = service.users().messages().list(userId='me', maxResults=5).execute().get('messages', [])
    email_data = [get_email_data(service, 'me', message['id']) for message in messages]

    # Return the email data as JSON
    return jsonify(email_data)


if __name__ == '__main__':
    app.run()
