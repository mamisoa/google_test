from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import base64
import os.path

# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

CRED_PATH = './env/credentials.json'
TOKEN = './env/token.json'

def authenticate():
    """
    Authenticates the user with OAuth2 and returns a Gmail API service client.

    Checks for existing credentials in 'credential.json'. If not found or invalid,
    a new token is generated after user authorization.

    Returns:
        service: Authorized Gmail API service client.
    """
    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_labels():
    """
    Authenticates the user and prints the list of Gmail labels.

    Calls the authenticate function to create a Gmail API service client and
    retrieves the list of labels (folders) in the user's Gmail account.
    """
    service = authenticate()
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

def get_subject_from_message(message):
    """
    Extracts the subject from a Gmail API message object.

    Args:
        message: Gmail API message object.

    Returns:
        subject: Subject string of the email.
    """
    headers = message['payload']['headers']
    for header in headers:
        if header['name'] == 'Subject':
            return header['value']

    return None

def read_latest_unread_email(service):
    """
    Reads the latest unread email from the user's Gmail account.

    Args:
        service: Authorized Gmail API service client.

    Returns:
        subject: Subject of the email.
        body: Body content of the email.
    """
    # Search for unread emails
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])

    if not messages:
        print('No unread messages found.')
        return None, None

    latest_message_info = messages[0]
    msg = service.users().messages().get(userId='me', id=latest_message_info['id']).execute()

    # Extracting the subject
    subject = None
    headers = msg['payload']['headers']
    for header in headers:
        if header['name'] == 'Subject':
            subject = header['value']

    # Extracting the body content
    part = msg['payload']['parts'][0]
    body_data = part['body']['data']
    body = base64.urlsafe_b64decode(body_data).decode('utf-8')

    # Optional: Marking the email as read
    service.users().messages().modify(userId='me', id=latest_message_info['id'], body={'removeLabelIds': ['UNREAD']}).execute()

    print(f"Message Subject: {subject}")
    print(f"Message Body: {body}")

    return subject, body

if __name__ == '__main__':
    service = authenticate()
    message = read_latest_unread_email(service)
    print("messsages:",message)
