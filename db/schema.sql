CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    sector TEXT,
    industry TEXT
);

CREATE TABLE profit_loss (
    company_id INTEGER,
    year INTEGER,
    revenue REAL,
    net_profit REAL,

    PRIMARY KEY(company_id, year),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE balance_sheet (
    company_id INTEGER,
    year INTEGER,

    total_assets REAL,
    total_liabilities REAL,
    equity REAL,

    PRIMARY KEY(company_id, year),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE cash_flow (
    company_id INTEGER,
    year INTEGER,

    operating_cf REAL,
    investing_cf REAL,
    financing_cf REAL,

    PRIMARY KEY(company_id, year),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE stock_prices (
    company_id INTEGER,
    price_date DATE,

    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,

    PRIMARY KEY(company_id, price_date),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE ratios (
    company_id INTEGER,
    year INTEGER,

    pe_ratio REAL,
    roe REAL,
    debt_equity REAL,
    operating_margin REAL,

    PRIMARY KEY(company_id, year),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE market_cap (
    company_id INTEGER,
    year INTEGER,

    market_cap REAL,

    PRIMARY KEY(company_id, year),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE shareholding (
    company_id INTEGER,
    year INTEGER,

    promoters REAL,
    fii REAL,
    dii REAL,
    public_shareholding REAL,

    PRIMARY KEY(company_id, year),

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE pros_cons (
    company_id INTEGER PRIMARY KEY,

    pros TEXT,
    cons TEXT,

    FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,

    sector_name TEXT UNIQUE
);
