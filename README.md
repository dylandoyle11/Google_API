
## Gspread and Google Drive API Wrapper

This Python package provides easy-to-use functionality for interacting with Google Sheets and Google Drive using the Gspread and PyDrive2 libraries. It provides classes for authenticating with Google Sheets and Google Drive API, uploading files to Google Drive, selecting a folder to upload files to, creating new folders, retrieving metadata for files, and listing files and folders.

## Usage
### GspreadAPI
The GspreadAPI class provides two methods for authenticating with Google Sheets API:

authenticate_personal(): Authenticates with Google Sheets API using personal credentials.
authenticate_service(): Authenticates with Google Sheets API using a service account.
For example:
```
from google_auth import GspreadAPI

# Authenticate using personal credentials
client_personal = GspreadAPI.authenticate_personal()

# Authenticate using a service account
client_service = GspreadAPI.authenticate_service()
```
Returns gspread object to be used with all existing gpsread methods.

### GoogleDriveAPI
The GoogleDriveAPI class provides methods for interacting with Google Drive API. 

```
from google_auth import GoogleDriveAPI

# Initialize the GoogleDriveAPI object
gdrive = GoogleDriveAPI(url="https://drive.google.com/drive/folders/<FOLDER_ID>")

# List all files in the given folder
files = gdrive.list_files_in_folder("<FOLDER_ID>")

# Upload a file to the current folder
uploaded_file = gdrive.upload_file(file_path="/path/to/file", file_name="file.txt")

# List all folders in the current directory
folders = gdrive.list_folders()

# Create a new folder
new_folder = gdrive.create_folder(folder_name="New Folder")

# Get the metadata for a specific file
file_metadata = gdrive.get_file_metadata(file_id="<FILE_ID>")
```

