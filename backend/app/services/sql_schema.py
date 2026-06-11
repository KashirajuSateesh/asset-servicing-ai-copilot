TABLE_SCHEMAS = {
    "custody_accounts": """
        CREATE TABLE custody_accounts (
            account_id NVARCHAR(50) PRIMARY KEY,
            account_name NVARCHAR(255),
            client_name NVARCHAR(255),
            account_type NVARCHAR(100),
            region NVARCHAR(100),
            currency NVARCHAR(10),
            status NVARCHAR(50),
            opened_date DATE
        );
    """,
    "trade_status": """
        CREATE TABLE trade_status (
            trade_id NVARCHAR(50) PRIMARY KEY,
            account_id NVARCHAR(50),
            security_id NVARCHAR(100),
            security_name NVARCHAR(255),
            trade_type NVARCHAR(50),
            quantity FLOAT,
            trade_amount FLOAT,
            currency NVARCHAR(10),
            trade_date DATE,
            settlement_date DATE,
            status NVARCHAR(100),
            counterparty NVARCHAR(255)
        );
    """,
    "settlement_exceptions": """
        CREATE TABLE settlement_exceptions (
            exception_id NVARCHAR(50) PRIMARY KEY,
            trade_id NVARCHAR(50),
            account_id NVARCHAR(50),
            exception_type NVARCHAR(255),
            severity NVARCHAR(50),
            status NVARCHAR(100),
            root_cause NVARCHAR(MAX),
            assigned_team NVARCHAR(100),
            created_at DATETIME2,
            sla_due_at DATETIME2
        );
    """,
    "reconciliation_breaks": """
        CREATE TABLE reconciliation_breaks (
            break_id NVARCHAR(50) PRIMARY KEY,
            account_id NVARCHAR(50),
            break_type NVARCHAR(255),
            amount_difference FLOAT,
            currency NVARCHAR(10),
            status NVARCHAR(100),
            priority NVARCHAR(50),
            aging_days INT,
            suspected_cause NVARCHAR(MAX),
            created_at DATETIME2
        );
    """,
    "case_tickets": """
        CREATE TABLE case_tickets (
            case_id NVARCHAR(50) PRIMARY KEY,
            related_id NVARCHAR(50),
            account_id NVARCHAR(50),
            case_type NVARCHAR(100),
            title NVARCHAR(255),
            description NVARCHAR(MAX),
            priority NVARCHAR(50),
            status NVARCHAR(100),
            owner NVARCHAR(100),
            created_at DATETIME2,
            updated_at DATETIME2
        );
    """,
    "corporate_actions": """
        CREATE TABLE corporate_actions (
            action_id NVARCHAR(50) PRIMARY KEY,
            account_id NVARCHAR(50),
            security_id NVARCHAR(100),
            action_type NVARCHAR(100),
            event_date DATE,
            payable_date DATE,
            status NVARCHAR(100),
            expected_amount FLOAT,
            currency NVARCHAR(10)
        );
    """,
}