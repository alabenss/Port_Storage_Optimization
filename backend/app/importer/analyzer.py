def classify_sheet(sheet_name):

    name = sheet_name.lower()


    if "véhicule" in name or "vehicule" in name:

        return "vehicle"


    if "conteneur" in name:

        return "container"


    if "remorque" in name:

        return "trailer"


    if "bl" in name:

        return "bill_of_lading"


    return "unknown"



def analyze_structure(sheets):

    result = {}

    summary = {

        "vehicles":0,

        "containers":0,

        "trailers":0,

        "bills_of_lading":0

    }


    for name,data in sheets.items():

        cargo_type = classify_sheet(name)


        result[name] = {

            "type": cargo_type,

            "rows": data["rows"],

            "columns": data["columns"]

        }


        if cargo_type=="vehicle":

            summary["vehicles"] = data["rows"]


        elif cargo_type=="container":

            summary["containers"] = data["rows"]


        elif cargo_type=="trailer":

            summary["trailers"] = data["rows"]


        elif cargo_type=="bill_of_lading":

            summary["bills_of_lading"] = data["rows"]



    return {

        "detected_structure": result,

        "summary": summary

    }