import os

Data = 'data/database.sqlite3'

def restore_backup(Data):
    try:
        # Constructing the filename for the backup by adding a "backup_" prefix to the database file's name
        name = "backup_" + os.path.splitext(os.path.basename(Data))[0]
        rename_data = os.path.join(os.path.dirname(Data), name) + ".sqlite3"
        #print(rename_data)
        # Checking if the backup exists
        if os.path.exists(rename_data):
            # Deleting the current database file
            os.remove(Data)
            # Renaming the backup to restore the database file
            os.rename(rename_data, Data)
        else:
            # Displaying an error message if no backup is found
            print("Impossible, there is no backup.")
            return False
    except FileNotFoundError:
        # Handling the error if the source file does not exist
        print("The file does not exist.")
    except PermissionError:
        # Handling the error if permission is denied to delete or rename the file
        print("Permission denied to delete the file.")
    except Exception as e:
        # Handling all other possible errors
        print(f"An error occurred: {e}")


restore_backup(Data)