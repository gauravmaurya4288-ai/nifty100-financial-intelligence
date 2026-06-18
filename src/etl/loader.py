import pandas as pd


def load_csv(file_path):
    return pd.read_csv(file_path)


def load_excel(file_path):
    return pd.read_excel(file_path)


def load_file(file_path):

    if file_path.endswith(".csv"):
        return load_csv(file_path)

    if file_path.endswith(".xlsx"):
        return load_excel(file_path)

    raise ValueError(
        f"Unsupported file type: {file_path}"
    )


if __name__ == "__main__":

    df = load_file(
        "data/raw/stock_prices.xlsx"
    )

    print(df.head())
    print(df.shape)