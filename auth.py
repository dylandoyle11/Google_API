import gspread
import json
from google.oauth2.service_account import Credentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import ApiRequestError
import inquirer
import os
import platform


class GspreadAPI:
    DEFAULT_SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    @classmethod
    def authenticate_personal(cls):
        client = gspread.oauth(scopes=cls.DEFAULT_SCOPES)
        return client

    @classmethod
    def authenticate_service(cls):
        with open('credentials.json', 'r') as f:
            credentials_data = json.load(f)

        creds = Credentials.from_service_account_info(credentials_data, scopes=cls.DEFAULT_SCOPES)
        client = gspread.authorize(creds)

        return client
    

class GoogleDriveAPI:
    """
    A class to interact with the Google Drive API.

    ...

    Attributes
    ----------
    gauth : pydrive2.auth.GoogleAuth
        An instance of the GoogleAuth class to authenticate Google Drive API
    drive : pydrive2.drive.GoogleDrive
        An instance of the GoogleDrive class to interact with Google Drive API
    folder_id : str
        The ID of the folder to upload files to

    Methods
    -------
    url_to_id(url):
        Parses the folder ID from a Google Drive folder URL
    authenticate():
        Authenticates with the Google Drive API and returns an authenticated GoogleAuth instance
    clear_terminal():
        Clears the terminal screen
    list_files_in_folder(folder_id):
        Returns a list of files in the specified folder
    upload_file(file_path, file_name, parent_folder_id=None):
        Uploads a file to Google Drive and returns the file object
    list_folders(parent_folder_id=None):
        Returns a list of folders in the specified folder ID or the root directory
    get_folder_path(folder_id, path=''):
        Returns the full path of the specified folder ID
    get_file_metadata(file_id):
        Returns the metadata of the specified file ID
    select_folder_and_upload(file_path, file_name):
        Prompts the user to select a folder to upload the file to and uploads the file to the selected folder
    create_folder(folder_name, parent_folder_id=None):
        Creates a new folder with the specified name in the specified parent folder ID or the root directory
    """

    DEFAULT_SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]


    def __init__(self, url=None):
        """
        Constructs all the necessary attributes for the GoogleDriveAPI object.

        Parameters
        ----------
            url : str, optional
                The URL of the folder to upload files to
        """
        self.gauth = self.authenticate()
        self.drive = GoogleDrive(self.gauth)
        self.folder_id = self.url_to_id(url)


    @staticmethod
    def url_to_id(url):
        """
        Parses the folder ID from a Google Drive folder URL

        Parameters
        ----------
        url : str
            The Google Drive folder URL

        Returns
        -------
        str
            The folder ID parsed from the URL or None if the URL is not valid
        """
        if url:
            return url.split('https://drive.google.com/drive/folders/')[-1]
        else:
            return None


    @staticmethod
    def authenticate():
        """
        Authenticates with the Google Drive API and returns an authenticated GoogleAuth instance

        Returns
        -------
        pydrive2.auth.GoogleAuth
            An instance of the GoogleAuth class to authenticate Google Drive API
        """
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("client_secrets.json")

        module_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(module_dir, "client_secrets.json")
        gauth.LoadCredentialsFile(credentials_path)

        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        gauth.SaveCredentialsFile("client_secrets.json")

        return gauth


    @staticmethod
    def clear_terminal():
        """
        Clears the terminal screen.
        """
        if platform.system().lower() == "windows":
            os.system("cls")
        else:
            os.system("clear")


    def list_files_in_folder(self, folder_id):
        """
        Lists all the files in a given folder.

        Args:
            folder_id (str): The ID of the folder to list files in.

        Returns:
            list of pydrive.drive.GoogleDriveFile: A list of files in the folder.
        """
        query = f"'{folder_id}' in parents and trashed=false"
        file_list = self.drive.ListFile({'q': query}).GetList()
        return file_list


    def upload_file(self, file_path, file_name, parent_folder_id=None):
        """
        Uploads a file to a given folder.

        Args:
            file_path (str): The path to the file to upload.
            file_name (str): The name of the file.
            parent_folder_id (str, optional): The ID of the folder to upload to. Defaults to None.

        Returns:
            pydrive.drive.GoogleDriveFile: The uploaded file.
        """
        file = self.drive.CreateFile({'title': file_name, 'parents': [{'id': parent_folder_id}]})
        file.SetContentFile(file_path)
        file.Upload()
        return file
    

    def list_folders(self, parent_folder_id=None):
        """
        Lists all the folders within the given parent folder.

        Args:
            parent_folder_id (str): ID of the parent folder. If not provided, the root folder is used.

        Returns:
            list: A list of dictionaries containing metadata of all the folders found within the parent folder.
                  Each dictionary contains the following keys: 'id', 'title', 'mimeType', 'createdDate',
                  'modifiedDate', 'parents', and 'permissions'.
        """

        query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        else:
            query += " and 'root' in parents"

        folders = []
        file_list = self.drive.ListFile({'q': query}).GetList()
        for file in file_list:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                folders.append({
                    'id': file['id'],
                    'title': file['title'],
                    'mimeType': file['mimeType'],
                    'createdDate': file['createdDate'],
                    'modifiedDate': file['modifiedDate'],
                    'parents': file['parents'],
                })

        return folders


    def get_folder_path(self, folder_id, path=''):
        """
        Returns the full path of the folder with the specified folder_id.

        Args:
            folder_id (str): The ID of the folder.
            path (str, optional): The path to the folder. Defaults to ''.

        Returns:
            str: The full path of the folder.
        """
        if folder_id is None or folder_id == 'root':
            return "My Drive" + path

        file = self.drive.CreateFile({'id': folder_id})
        file.FetchMetadata(fields='parents, title, mimeType, capabilities')

        # Check if the current folder is the root of a shared drive
        if 'capabilities' in file and file['capabilities']['canAddChildren'] == False and 'parents' not in file:
            return "Shared Drive: " + file['title'] + path

        if 'parents' in file and len(file['parents']) > 0:
            parent_id = file['parents'][0]['id']
            parent_path = self.get_folder_path(parent_id, os.path.join(file['title'], path))
            return parent_path
        else:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                return os.path.join(file['title'], path)
            else:
                return path


    def get_file_metadata(self, file_id):
        """
        Retrieve metadata for a file with the given ID.

        Args:
            file_id (str): ID of the file to retrieve metadata for.

        Returns:
            pydrive.drive.GoogleDriveFile: The file object containing the file metadata.

        Raises:
            pydrive.auth.AuthenticationError: If the authentication process fails.
            pydrive.files.ApiRequestError: If the request to retrieve file metadata fails.
        """
        file = self.drive.CreateFile({'id': file_id})
        try:
            file.FetchMetadata()
        except ApiRequestError as e:
            raise e
        return file


    def select_folder_and_upload(self, file_path: str, file_name: str) -> str:
        """
        Select a folder to upload a file to and upload the file.

        Args:
            file_path (str): The path to the file to upload.
            file_name (str): The name to give the uploaded file.

        Returns:
            str: The full path of the uploaded file.

        """
        while True:
            self.clear_terminal()
            folders = self.list_folders(self.folder_id)
            folder_choices = [folder['title'] for folder in folders]
            folder_choices.insert(0, 'Create a new folder')
            folder_choices.insert(0, 'Upload to current folder')
            folder_choices.insert(0, 'Go back to parent folder')
            current_directory = self.get_folder_path(self.folder_id)

            print("\nCurrent directory: {}\n".format(current_directory))

            questions = [
                inquirer.List(
                    'folder',
                    message='Select a folder to upload the file:',
                    choices=folder_choices,
                )
            ]
            selected_folder_title = inquirer.prompt(questions)['folder']

            if selected_folder_title == 'Go back to parent folder':
                if self.folder_id:
                    parent_folder = self.get_file_metadata(self.folder_id)
                    self.folder_id = parent_folder['parents'][0]['id'] if parent_folder['parents'] else None
            elif selected_folder_title == 'Create a new folder':
                new_folder_name = input("Enter the name of the new folder: ")
                new_folder = self.create_folder(new_folder_name, self.folder_id)
                print(f'Created New Folder: {new_folder_name}')
                self.folder_id = new_folder['id']
            elif selected_folder_title == 'Upload to current folder':
                uploaded_file = self.upload_file(file_path, file_name, self.folder_id)
                uploaded_file_path = self.get_folder_path(self.folder_id)
                uploaded_file_path = os.path.join(uploaded_file_path, file_name)
                return uploaded_file_path
            else:
                selected_folder = next(folder for folder in folders if folder['title'] == selected_folder_title)
                self.folder_id = selected_folder['id']
            

    def create_folder(self, folder_name, parent_folder_id=None):
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_folder_id:
            folder_metadata['parents'] = [{'id': parent_folder_id}]

        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()

        return folder

'''

TODO: INTEGRATE SECRETS MANAGER
figure out how to use a service accounts

from GspreadAuth import GspreadAuth

SAMPLE USAGE:

# authenticate with personal credentials
gc_personal = GspreadAuth.authenticate_personal()

# authenticate with service account credentials
gc_service = GspreadAuth.authenticate_service()

# open a spreadsheet
spreadsheet_key = '<your-spreadsheet-key>'
worksheet_name = '<your-worksheet-name>'

# open the worksheet using personal credentials
worksheet_personal = gc_personal.open_by_key(spreadsheet_key).worksheet(worksheet_name)

# open the worksheet using service account credentials
worksheet_service = gc_service.open_by_key(spreadsheet_key).worksheet(worksheet_name)
    
'''