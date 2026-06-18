def normalize_year(value):
    if value is None:
        return None

    return int(str(value).strip())


def normalize_ticker(value):
    if value is None:
        return None

    return str(value).strip().upper()


def normalize_text(value):
    if value is None:
        return None

    return str(value).strip()


def normalize_currency(value):
    if value is None:
        return None

    return float(str(value).replace(",", "").strip())


def normalize_percentage(value):
    if value is None:
        return None

    return float(str(value).replace("%", "").strip())