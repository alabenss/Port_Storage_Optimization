from app.importer.excel_reader import read_manifest
from app.importer.analyzer import analyze_structure



def generate_preview(path):

    sheets = read_manifest(path)

    analysis = analyze_structure(
        sheets
    )


    preview = {

        "file_ready": True,

        "summary": analysis["summary"],

        "detected_structure": analysis["detected_structure"],

        "warnings": []

    }


    # Basic validation

    vehicle_count = analysis["summary"]["vehicles"]

    if vehicle_count > 0:

        preview["warnings"].append(
            f"{vehicle_count} vehicles detected"
        )


    container_count = analysis["summary"]["containers"]

    if container_count > 0:

        preview["warnings"].append(
            f"{container_count} containers detected"
        )


    return preview