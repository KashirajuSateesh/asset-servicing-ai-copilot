TABLE_SCHEMAS = {
    "custody_accounts": """
        CREATE TABLE custody_accounts (
            account_id NVARCHAR(50) PRIMARY KEY,
            client_name NVARCHAR(255),
            client_type NVARCHAR(100),
            custodian NVARCHAR(100),
            region NVARCHAR(100),
            base_currency NVARCHAR(10),
            risk_level NVARCHAR(50),
            account_status NVARCHAR(50),
            onboarded_date DATE,
            relationship_owner NVARCHAR(100),
            kyc_review_due DATE
        );
    """,
    "trade_status": """
        CREATE TABLE trade_status (
            trade_id NVARCHAR(50) PRIMARY KEY,
            account_id NVARCHAR(50),
            security_id NVARCHAR(100),
            security_type NVARCHAR(100),
            trade_date DATE,
            settlement_date DATE,
            side NVARCHAR(50),
            quantity FLOAT,
            price FLOAT,
            gross_amount FLOAT,
            currency NVARCHAR(10),
            counterparty NVARCHAR(255),
            trade_status NVARCHAR(100),
            last_updated DATETIME2,
            settlement_location NVARCHAR(100)
        );
    """,
    "settlement_exceptions": """
        CREATE TABLE settlement_exceptions (
            exception_id NVARCHAR(50) PRIMARY KEY,
            trade_id NVARCHAR(50),
            account_id NVARCHAR(50),
            exception_reason NVARCHAR(255),
            severity NVARCHAR(50),
            detected_date DATETIME2,
            sla_due_date DATETIME2,
            assigned_team NVARCHAR(100),
            exception_status NVARCHAR(100),
            resolution_notes NVARCHAR(MAX),
            estimated_exposure_usd FLOAT
        );
    """,
    "reconciliation_breaks": """
        CREATE TABLE reconciliation_breaks (
            break_id NVARCHAR(50) PRIMARY KEY,
            account_id NVARCHAR(50),
            break_date DATE,
            break_type NVARCHAR(255),
            source_system NVARCHAR(100),
            book_amount FLOAT,
            custody_amount FLOAT,
            variance_amount FLOAT,
            currency NVARCHAR(10),
            aging_days INT,
            owner_team NVARCHAR(100),
            break_status NVARCHAR(100),
            root_cause NVARCHAR(MAX)
        );
    """,
    "case_tickets": """
        CREATE TABLE case_tickets (
            case_id NVARCHAR(50) PRIMARY KEY,
            account_id NVARCHAR(50),
            category NVARCHAR(100),
            linked_record_id NVARCHAR(50),
            created_date DATETIME2,
            priority NVARCHAR(50),
            case_status NVARCHAR(100),
            requestor NVARCHAR(100),
            assigned_team NVARCHAR(100),
            subject NVARCHAR(255),
            case_summary NVARCHAR(MAX),
            last_touch_date DATETIME2,
            sla_status NVARCHAR(100)
        );
    """,
    "corporate_actions": """
        CREATE TABLE corporate_actions (
            corporate_action_id NVARCHAR(50) PRIMARY KEY,
            account_id NVARCHAR(50),
            security_id NVARCHAR(100),
            action_type NVARCHAR(100),
            announcement_date DATE,
            ex_date DATE,
            record_date DATE,
            payable_date DATE,
            election_deadline DATE,
            status NVARCHAR(100),
            entitlement_amount FLOAT,
            currency NVARCHAR(10),
            custody_notes NVARCHAR(MAX)
        );
    """,
}