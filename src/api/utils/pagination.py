import math


def paginate(total_records, page, page_size):

    total_pages = math.ceil(total_records / page_size)

    offset = (page - 1) * page_size

    return {
        "offset": offset,
        "limit": page_size,
        "total_pages": total_pages,
    }