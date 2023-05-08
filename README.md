
Gspread and Google Drive API
This Python package provides easy-to-use functionality for interacting with Google Sheets and Google Drive using the Gspread and PyDrive2 libraries. It provides classes for authenticating with Google Sheets and Google Drive API, uploading files to Google Drive, selecting a folder to upload files to, creating new folders, retrieving metadata for files, and listing files and folders.

## Usage
GspreadAPI
The GspreadAPI class provides two methods for authenticating with Google Sheets API:

authenticate_personal(): Authenticates with Google Sheets API using personal credentials.
authenticate_service(): Authenticates with Google Sheets API using a service account.
For example:
```
from gspread_api import GspreadAPI

# Authenticate using personal credentials
client_personal = GspreadAPI.authenticate_personal()

# Authenticate using a service account
client_service = GspreadAPI.authenticate_service()
```

GoogleDriveAPI
The GoogleDriveAPI class provides methods for interacting with Google Drive API. The following methods are available:

authenticate(): Authenticates with Google Drive API and returns an authenticated GoogleAuth instance.
url_to_id(url): Parses the folder ID from a Google Drive folder URL.
list_files_in_folder(folder_id): Returns a list of files in the specified folder ID.
upload_file(file_path, file_name, parent_folder_id=None): Uploads a file to Google Drive and returns the file object.
list_folders(parent_folder_id=None): Returns a list of folders in the specified folder ID or the root directory.
get_folder_path(folder_id, path=''): Returns the full path of the specified folder ID.
get_file_metadata(file_id): Returns the metadata of the specified file ID.
select_folder_and_upload(file_path, file_name): Prompts the user to select a folder to upload the file to and uploads the file to the selected folder.
create_folder(folder_name, parent_folder_id=None): Creates a new folder with the specified name in the specified parent folder ID or the root directory.
