from __future__ import print_function
import pickle
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

# """Shows basic usage of the Drive v3 API.
# Prints the names and ids of the first 10 files the user has access to.
# """
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "./json_files/google_client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.pickle", 'wb') as token:
        pickle.dump(creds, token)

drive_service = build("drive", "v3", credentials=creds)


def uploadFile(filename, filepath, mimetype):
    file_metadata = {"name": filename}
    media = MediaFileUpload(filepath,
                            mimetype=mimetype)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields="id").execute()
    print("File ID: %s" % file.get("id"))


def listFiles(size):
    results = drive_service.files().list(
        pageSize=size, fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])
    if not items:
        print("No files found.")
    else:
        print("Files:")
        for item in items:
            print("{0} ({1})".format(item["name"], item["id"]))


def downloadFile(file_id, filepath):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(filepath, "wb") as f:
        fh.seek(0)
        f.write(fh.read())


def createFolder(name):
    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    file = drive_service.files().create(body=file_metadata,
                                        fields="id").execute()
    print("Folder ID: %s" % file.get("id"))


def searchFile(size, query):
    results = drive_service.files().list(
        pageSize=size, fields="nextPageToken, files(id, name, kind, mimeType)", q=query).execute()
    items = results.get("files", [])
    if not items:
        print("No files found.")
    else:
        print("Files:")
        for item in items:
            print(item)
            print(f"{item['name']} ({item['id']})")


# query is the name of the folder, returns the folder's ID
def getFolderID(query):
    page_token, folderID = None, None
    while True:
        response = drive_service.files().list(q=f"name='{query}' and mimeType='application/vnd.google-apps.folder'",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            # process change
            page_token = response.get('nextPageToken', None)
            folderID = file.get('id')
            if page_token is None:
                break
        return folderID
    # if no match, function returns NoneType
    # if there is match, function returns string


# returns the folder ID of the newly created folder
# takes in the filename of the new folder and the ID of the parent folder as arguments
def createFolderinFolder(filename, parent_folder_id):
    file_metadata = {
        'name': [filename],
        'parents': [parent_folder_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()
    folderID = file.get('id')
    return folderID


# filename is the name of the file, filepath is the file that you're uploading
# parent_id is the ID of the folder you're uploading to
# folder IDs can be gotten from the function getFolderID
def uploadFiletoFolder(filename, filepath, parent_id):
    file_metadata = {
        'name': filename,
        'parents': [parent_id],
        # 'mimeType': 'application/vnd.google-apps.file'
    }
    media = MediaFileUpload(filepath,
                            resumable=True)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    fileID = file.get('id')
    print(f"{filename} uploaded, file ID is {fileID}")