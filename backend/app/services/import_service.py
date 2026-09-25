import pandas as pd
import unicodedata


INVALID_VALUES = {
    "",
    "EOF",
    "CODE",
    "NAN",
    "NONE",
    "NULL"
}


def clean_text(value):

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    value = str(value).strip()

    if value.upper() in INVALID_VALUES:
        return None

    return value


def normalize(value):

    if value is None:
        return ""

    return (
        unicodedata.normalize(
            "NFD",
            str(value)
        )
        .encode(
            "ascii",
            "ignore"
        )
        .decode()
        .lower()
        .replace(" ", "")
        .replace("\t", "")
        .replace("°", "")
        .replace("/", "")
        .replace("-", "")
        .replace("_", "")
        .replace("'", "")
    )


def normalize_columns(df):

    df.columns = [
        str(column)
        .replace("\t", "")
        .strip()
        for column in df.columns
    ]

    return df


def find_column(columns, keywords):

    for column in columns:

        normalized_column = normalize(column)

        for keyword in keywords:

            if normalize(keyword) in normalized_column:
                return column

    return None


def read_real_sheet(file_path, sheet):

    selected = None

    for header_row in range(5):

        try:

            df = pd.read_excel(
                file_path,
                sheet_name=sheet,
                header=header_row
            )

            df = normalize_columns(df)

            if selected is None:
                selected = df

            combined_columns = "".join(
                normalize(column)
                for column in df.columns
            )

            if (
                "nbl" in combined_columns
                or "nchassis" in combined_columns
                or "ntc" in combined_columns
            ):
                return df

        except Exception:
            continue

    if selected is not None:
        return selected

    return pd.DataFrame()


def safe_number(value):

    if value is None:
        return None

    try:

        if pd.isna(value):
            return None

    except Exception:
        pass

    if isinstance(value, str):

        value = (
            value
            .replace(" ", "")
            .replace(",", ".")
        )

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def safe_integer(value):

    number = safe_number(value)

    if number is None:
        return None

    try:
        return int(number)

    except (TypeError, ValueError):
        return None


def row_preview(row, mapping):

    result = {}

    for output_name, column_name in mapping.items():

        if column_name is None:
            result[output_name] = None
            continue

        value = row.get(column_name)

        if output_name in {
            "weight",
            "gross_weight",
            "loaded_weight"
        }:
            result[output_name] = safe_number(value)

        elif output_name in {
            "quantity",
            "package_number",
            "year"
        }:
            result[output_name] = safe_integer(value)

        else:
            result[output_name] = clean_text(value)

    return result


def analyze_manifest(file_path):

    excel = pd.ExcelFile(file_path)

    preview = {

        "file_valid": True,

        "sheets": excel.sheet_names,

        "summary": {
            "bill_of_lading": 0,
            "vehicles": 0,
            "containers": 0,
            "trailers": 0
        },

        "records": {
            "bill_of_lading": [],
            "vehicles": [],
            "containers": [],
            "trailers": []
        },

        "validation": {
            "warnings": [],
            "errors": []
        }
    }

    # =====================================================
    # BILL OF LADING
    # =====================================================

    if "BL" in excel.sheet_names:

        df = read_real_sheet(
            file_path,
            "BL"
        )

        bl_col = find_column(
            df.columns,
            [
                "N° B/L",
                "BL"
            ]
        )

        nature_col = find_column(
            df.columns,
            [
                "Nature De Marchandise",
                "Nature de cargaison",
                "Nature"
            ]
        )

        description_col = find_column(
            df.columns,
            [
                "Description commerciale",
                "Description"
            ]
        )

        weight_col = find_column(
            df.columns,
            [
                "Poids Brut",
                "Poids"
            ]
        )

        package_col = find_column(
            df.columns,
            [
                "Nombre colis",
                "Nbr colis",
                "Package"
            ]
        )

        if not bl_col:

            preview["validation"]["errors"].append(
                "BL sheet found but Bill of Lading column was not detected."
            )

        else:

            seen = set()

            for _, row in df.iterrows():

                bl_number = clean_text(
                    row.get(bl_col)
                )

                if not bl_number:
                    continue

                if bl_number in seen:

                    preview["validation"]["warnings"].append(
                        f"Duplicate BL in Excel file: {bl_number}"
                    )

                    continue

                seen.add(bl_number)

                record = row_preview(
                    row,
                    {
                        "bl_number": bl_col,
                        "cargo_nature": nature_col,
                        "description": description_col,
                        "gross_weight": weight_col,
                        "package_number": package_col
                    }
                )

                preview["records"]["bill_of_lading"].append(
                    record
                )

    else:

        preview["validation"]["errors"].append(
            "Required sheet 'BL' was not found."
        )

    # =====================================================
    # VEHICLES
    # =====================================================

    if "Véhicule" in excel.sheet_names:

        df = read_real_sheet(
            file_path,
            "Véhicule"
        )

        bl_col = find_column(
            df.columns,
            ["N° B/L"]
        )

        chassis_col = find_column(
            df.columns,
            [
                "N° châssis du véhicule",
                "châssis",
                "chassis"
            ]
        )

        registration_col = find_column(
            df.columns,
            [
                "immatriculation"
            ]
        )

        manufacturer_col = find_column(
            df.columns,
            [
                "fabricant",
                "Code du fabricant"
            ]
        )

        model_col = find_column(
            df.columns,
            [
                "modèle",
                "modele",
                "Code du modèle"
            ]
        )

        type_col = find_column(
            df.columns,
            [
                "Type de véhicule",
                "Type"
            ]
        )

        year_col = find_column(
            df.columns,
            [
                "Année de fabrication",
                "Annee"
            ]
        )

        weight_col = find_column(
            df.columns,
            [
                "Poids total en charge",
                "Poids"
            ]
        )

        if not chassis_col:

            preview["validation"]["warnings"].append(
                "Vehicle sheet found but chassis column was not detected."
            )

        else:

            seen = set()

            for _, row in df.iterrows():

                chassis = clean_text(
                    row.get(chassis_col)
                )

                if not chassis:
                    continue

                if chassis in seen:

                    preview["validation"]["warnings"].append(
                        f"Duplicate vehicle chassis in Excel file: {chassis}"
                    )

                    continue

                seen.add(chassis)

                record = row_preview(
                    row,
                    {
                        "bl_number": bl_col,
                        "chassis_number": chassis_col,
                        "registration_number": registration_col,
                        "manufacturer": manufacturer_col,
                        "model": model_col,
                        "vehicle_type": type_col,
                        "year": year_col,
                        "loaded_weight": weight_col
                    }
                )

                preview["records"]["vehicles"].append(
                    record
                )

    # =====================================================
    # CONTAINERS
    # =====================================================

    if "Conteneur" in excel.sheet_names:

        df = read_real_sheet(
            file_path,
            "Conteneur"
        )

        bl_col = find_column(
            df.columns,
            ["N° B/L"]
        )

        number_col = find_column(
            df.columns,
            [
                "N° TC",
                "Container"
            ]
        )

        category_col = find_column(
            df.columns,
            [
                "Catégorie",
                "Categorie",
                "Type"
            ]
        )

        package_col = find_column(
            df.columns,
            [
                "Nombre colis",
                "Package"
            ]
        )

        weight_col = find_column(
            df.columns,
            [
                "Poids Brut",
                "Poids"
            ]
        )

        if not number_col:

            preview["validation"]["warnings"].append(
                "Container sheet found but container number column was not detected."
            )

        else:

            seen = set()

            for _, row in df.iterrows():

                container_number = clean_text(
                    row.get(number_col)
                )

                if not container_number:
                    continue

                if container_number in seen:

                    preview["validation"]["warnings"].append(
                        f"Duplicate container in Excel file: {container_number}"
                    )

                    continue

                seen.add(container_number)

                record = row_preview(
                    row,
                    {
                        "bl_number": bl_col,
                        "container_number": number_col,
                        "category": category_col,
                        "package_number": package_col,
                        "gross_weight": weight_col
                    }
                )

                preview["records"]["containers"].append(
                    record
                )

    # =====================================================
    # TRAILERS
    # =====================================================

    if "Remorque" in excel.sheet_names:

        df = read_real_sheet(
            file_path,
            "Remorque"
        )

        bl_col = find_column(
            df.columns,
            ["N° B/L"]
        )

        reference_col = find_column(
            df.columns,
            [
                "N° châssis",
                "Référence",
                "Reference"
            ]
        )

        type_col = find_column(
            df.columns,
            ["Type"]
        )

        weight_col = find_column(
            df.columns,
            ["Poids"]
        )

        if not reference_col:

            preview["validation"]["warnings"].append(
                "Trailer sheet found but trailer reference column was not detected."
            )

        else:

            seen = set()

            for _, row in df.iterrows():

                reference = clean_text(
                    row.get(reference_col)
                )

                if not reference:
                    continue

                if reference in seen:

                    preview["validation"]["warnings"].append(
                        f"Duplicate trailer in Excel file: {reference}"
                    )

                    continue

                seen.add(reference)

                record = row_preview(
                    row,
                    {
                        "bl_number": bl_col,
                        "reference": reference_col,
                        "trailer_type": type_col,
                        "weight": weight_col
                    }
                )

                preview["records"]["trailers"].append(
                    record
                )

    # =====================================================
    # SUMMARY
    # =====================================================

    for key in preview["summary"]:

        preview["summary"][key] = len(
            preview["records"][key]
        )

    preview["summary"]["total_records"] = sum(
        preview["summary"].values()
    )

    if preview["validation"]["errors"]:
        preview["file_valid"] = False

    return preview