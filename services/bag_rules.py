BAG_ALLOWED = {
    "pending": ["opened"],
    "opened": ["settled"],
    "settled": [],
}


def can_change_bag_status(old_status, new_status):

    allowed = BAG_ALLOWED.get(old_status, [])

    return new_status in allowed
