from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

import os
import shutil

from app.services.import_service import analyze_manifest

from app.services.upload_manager import (
    register_upload,
    get_upload
)


router = APIRouter()


UPLOAD_DIR = "uploads"


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@router.post("/manifest")
async def import_manifest(
    file: UploadFile = File(...)
):

    filename = os.path.basename(
        file.filename or "manifest.xlsx"
    )

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in {
        ".xlsx",
        ".xls"
    }:

        raise HTTPException(
            status_code=400,
            detail="Only Excel manifest files (.xlsx or .xls) are supported."
        )

    path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    try:

        with open(
            path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        preview = analyze_manifest(
            path
        )

    except Exception as exc:

        if os.path.exists(path):
            os.remove(path)

        raise HTTPException(
            status_code=400,
            detail=f"Unable to analyze manifest: {exc}"
        )

    upload_id = register_upload(
        filename=filename,
        path=path,
        preview=preview
    )

    return {

        "status":
            "MANIFEST_ANALYZED",

        "upload_id":
            upload_id,

        "original_filename":
            filename,

        "can_import":
            preview["file_valid"],

        "preview":
            preview
    }


@router.post("/confirm")
def confirm_import(
    upload_id: str
):

    from app.database.database import SessionLocal

    from app.importer.database_importer import (
        import_manifest_to_database
    )

    upload = get_upload(
        upload_id
    )

    if not upload:

        raise HTTPException(
            status_code=404,
            detail="Upload not found"
        )

    preview = upload.get(
        "preview"
    )

    if (
        preview
        and not preview.get(
            "file_valid",
            True
        )
    ):

        raise HTTPException(
            status_code=400,
            detail={
                "message":
                    "Manifest validation failed. Import was not executed.",

                "validation":
                    preview.get(
                        "validation",
                        {}
                    )
            }
        )

    db = SessionLocal()

    try:

        result = import_manifest_to_database(
            db,
            upload["path"]
        )

        return {

            "status":
                "IMPORT_COMPLETED",

            "file":
                upload["filename"],

            "upload_id":
                upload_id,

            "imported":
                result
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Manifest import failed: {exc}"
        )

    finally:

        db.close()