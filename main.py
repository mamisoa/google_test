from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os.path

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
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

def main():
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

if __name__ == '__main__':
    main()
