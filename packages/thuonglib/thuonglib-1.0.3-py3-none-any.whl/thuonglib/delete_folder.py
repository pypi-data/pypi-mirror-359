def d_folder(path_folder):
    import os
    if path_folder and os.path.exists(path_folder):
        for root, dirs, files in os.walk(path_folder, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete file {file_path}: {e}")
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    # Only remove empty directories
                    os.rmdir(dir_path)
                    print(f"Deleted directory: {dir_path}")
                except Exception as e:
                    print(f"Failed to clean {path_folder}: {e}")