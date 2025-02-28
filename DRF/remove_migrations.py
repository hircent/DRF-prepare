import os
import shutil

def clean_django_project():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of manage.py

    # Recursively walk through the project directory
    for root, dirs, files in os.walk(base_dir):
        # Remove __pycache__ folders
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            shutil.rmtree(pycache_path)
            print(f"Removed: {pycache_path}")

        # Remove migration files except __init__.py (Only inside "migrations" folders)
        if "migrations" in root.split(os.sep):  
            for file in files:
                if file != "__init__.py":
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    print(f"Removed: {file_path}")

if __name__ == "__main__":
    clean_django_project()
