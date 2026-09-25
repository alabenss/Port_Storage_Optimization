def weight_valid(cargo,position):

    return (
        cargo.weight
        <=
        position.max_weight
    )