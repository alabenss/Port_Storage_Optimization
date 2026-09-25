import os
import uuid


UPLOADS = {}


def register_upload(
    filename,
    path,
    preview
):

    upload_id = str(uuid.uuid4())

    UPLOADS[upload_id] = {

        "filename": filename,

        "path": path,

        "preview": preview

    }

    return upload_id



def get_upload(upload_id):

    return UPLOADS.get(upload_id)



def delete_upload(upload_id):

    if upload_id in UPLOADS:

        del UPLOADS[upload_id]