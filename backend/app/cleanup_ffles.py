# A script to clean up orphaned files in the upload directory

import os

from app import app
from app.models import Abstracts

with app.app_context():
    # Get all PDF abstracts
    pdf_abstracts = Abstracts.query.filter_by(file_type="pdf").all()
    existing_files = {abs.file_path for abs in pdf_abstracts if abs.file_path}

    # Find orphaned files
    upload_dir = app.config["UPLOAD_FOLDER"]
    for user_dir in os.listdir(upload_dir):
        user_path = os.path.join(upload_dir, user_dir)
        if os.path.isdir(user_path):
            for filename in os.listdir(user_path):
                file_rel_path = os.path.join(user_dir, filename)
                if file_rel_path not in existing_files:
                    print(f"Orphaned file: {file_rel_path}")
                    os.remove(os.path.join(upload_dir, file_rel_path))
