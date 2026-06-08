VIRTUAL_ALLOWED = {
    "pending": ["paid", "failed"],
    "paid": ["issued", "refunded"],
    "issued": [],
    "failed": [],
    "refunded": [],
}


PHYSICAL_ALLOWED = {
    "pending": ["paid", "failed"],
    "paid": ["shipped", "refunded"],
    "shipped": ["delivered"],
    "delivered": [],
    "failed": [],
    "refunded": [],
}


def can_change_status(product_type, old_status, new_status):

    if product_type == "virtual":
        rules = VIRTUAL_ALLOWED
    else:
        rules = PHYSICAL_ALLOWED

    allowed = rules.get(old_status, [])

    return new_status in allowed
