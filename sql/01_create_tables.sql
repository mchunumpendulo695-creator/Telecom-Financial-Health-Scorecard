-- ============================================================
-- Telecom Risk Project
-- 01_create_tables.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS telecom_project;

USE telecom_project;

-- Main financial dataset
CREATE TABLE IF NOT EXISTS telecom_financials (
    company VARCHAR(50) NOT NULL,
    fiscal_year INT NOT NULL,
    revenue_zar_m DECIMAL(15,2),
    ebitda_zar_m DECIMAL(15,2),
    net_profit_loss_zar_m DECIMAL(15,2),
    subscribers_m DECIMAL(10,2),
    arpu_zar DECIMAL(10,2),
    audit_notes TEXT,
    sourced_document TEXT,
    PRIMARY KEY (company, fiscal_year)
);