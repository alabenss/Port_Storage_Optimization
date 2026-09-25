import pandas as pd


file_path = "uploads/Déclaration  de cargaison_26_10_2025_13_46(MV  ESTRELLA).xlsx"


excel = pd.ExcelFile(file_path)


print("SHEETS:")
print(excel.sheet_names)


for sheet in excel.sheet_names:

    print("\n====================")
    print("SHEET:", sheet)

    df = pd.read_excel(
        file_path,
        sheet_name=sheet,
        header=None
    )


    print("SIZE:")
    print(df.shape)


    print("FIRST 10 ROWS:")
    print(df.head(10).to_string())