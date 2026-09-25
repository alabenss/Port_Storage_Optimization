def validate_vehicle(row):

    errors=[]


    if not row.get(
        "chassis_number"
    ):

        errors.append(
            "Missing chassis number"
        )


    if not row.get(
        "weight"
    ):

        errors.append(
            "Missing weight"
        )


    return errors



def validate_dataframe(df):

    results=[]


    for index,row in df.iterrows():

        errors=validate_vehicle(
            row
        )


        if errors:

            results.append({

                "row":index,

                "errors":errors

            })


    return results