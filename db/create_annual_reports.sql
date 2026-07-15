DROP TABLE IF EXISTS annual_reports;

CREATE TABLE annual_reports (

    company_id TEXT NOT NULL,

    company_name TEXT NOT NULL,

    year TEXT NOT NULL,

    report_url TEXT,

    status TEXT DEFAULT 'Unavailable',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY(company_id, year)

);