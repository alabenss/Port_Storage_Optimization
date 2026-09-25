import pandas as pd


file = "uploads/Déclaration  de cargaison_26_10_2025_13_46(MV  ESTRELLA).xlsx"


excel = pd.ExcelFile(file)


print("SHEETS:")
print(excel.sheet_names)



for sheet in excel.sheet_names:

    print("\n====================")
    print(sheet)
    print("====================")


    df = pd.read_excel(
        file,
        sheet_name=sheet,
        header=1
    )


    print("ROWS:",len(df))
    print("COLUMNS:")
    print(df.columns.tolist())


    print("\nFIRST 5 ROWS:")
    print(df.head())