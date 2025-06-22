-- src/database/schema.sql

-- Table to store time series data for economic activity indexes from BCB SGS
-- This table can be expanded later with more series or more granular regional data.

CREATE TABLE IF NOT EXISTS bcb_economic_activity_index (
    series_date DATE PRIMARY KEY,                     -- Date of the observation
    ibc_br_national DECIMAL(10, 2),               -- National IBC-Br index value
    ibcr_northeast_regional DECIMAL(10, 2),       -- Northeast IBCR-NE index value
    -- Potential future columns:
    -- ibc_pe_state DECIMAL(10,2),                 -- Placeholder if a Pernambuco specific IBC is found
    -- other_regional_indexes...
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- To track when the record was last updated
);

COMMENT ON TABLE bcb_economic_activity_index IS 'Stores economic activity indexes from the Brazilian Central Bank (BCB) Time Series Management System (SGS). Includes national IBC-Br and regional IBCR-NE.';
COMMENT ON COLUMN bcb_economic_activity_index.series_date IS 'Date of the index observation (YYYY-MM-DD). Typically monthly for these series.';
COMMENT ON COLUMN bcb_economic_activity_index.ibc_br_national IS 'National Economic Activity Index - IBC-Br (seasonally adjusted). Source: BCB SGS Code 24363.';
COMMENT ON COLUMN bcb_economic_activity_index.ibcr_northeast_regional IS 'Regional Economic Activity Index - Northeast (IBCR-NE, seasonally adjusted). Source: BCB SGS Code 25380.';
COMMENT ON COLUMN bcb_economic_activity_index.last_updated IS 'Timestamp of when this row was last inserted or updated in the database.';

-- Example of how data might be inserted (conceptual, actual loading will be via Python script):
-- INSERT INTO bcb_economic_activity_index (series_date, ibc_br_national, ibcr_northeast_regional)
-- VALUES ('2023-01-01', 145.60, 150.20);

-- Note: DECIMAL(10, 2) assumes index values will fit this precision. Adjust if needed based on actual data range.
-- The SGS series often have varying decimal places, so storing them with a fixed precision might be necessary.
-- Consider using FLOAT or DOUBLE PRECISION if the exact decimal places are not critical and for simpler handling,
-- but DECIMAL is better for financial/economic data where precision matters.
-- The choice also depends on the specific database system (e.g., PostgreSQL, MySQL).
-- For example, in PostgreSQL, NUMERIC(10,2) is equivalent to DECIMAL(10,2).
