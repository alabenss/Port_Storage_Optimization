import pandas as pd


def detect_header_row(path, sheet):

    preview = pd.read_excel(
        path,
        sheet_name=sheet,
        header=None,
        nrows=10
    )


    keywords = [
        "chassis",
        "poids",
        "weight",
        "container",
        "conteneur",
        "code",
        "date",
        "nature"
    ]


    for index,row in preview.iterrows():

        row_text = " ".join(
            str(x).lower()
            for x in row.values
        )


        matches = sum(
            1
            for k in keywords
            if k in row_text
        )


        if matches >= 1:

            return index


    return 0



def read_manifest(path):

    excel = pd.ExcelFile(path)

    result = {}


    for sheet in excel.sheet_names:


        header = detect_header_row(
            path,
            sheet
        )


        df = pd.read_excel(
            path,
            sheet_name=sheet,
            header=header
        )


        result[sheet] = {

            "data": df,

            "rows": len(df),

            "columns": list(df.columns)

        }


    return result