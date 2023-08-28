import os

def rename_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for fname in files:
            if fname != "removepoint.py":
                newName = ""
                filename_without_extension, file_extension = os.path.splitext(fname)
                for char in filename_without_extension:
                    if char != '.':
                        newName += char
                old_filepath = os.path.join(root, fname)
                new_filepath = os.path.join(root, newName + file_extension)
                print(str(old_filepath) + " ==>> " + str(new_filepath))
                os.rename(old_filepath, new_filepath)

current_path = os.path.dirname(__file__)
print("DIR : " + current_path)

print("=====  OR file  =====")
rename_files_in_directory(current_path)
print("=====  =======  =====")
