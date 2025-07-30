import os
from pathlib import Path

PATH_PROJECT = Path(__file__).parent

# test
# user = "arnaud.alepee@qonto.com"
user = "gauthier.marquand@qonto.com"

# Email from which we gather the inventory files
dict_mailbox_adress_password = {
    "gauthier.marquand@qonto.com": "umsu usvk gqjx rxwc",
    "arnaud.alepee@qonto.com": "vhyk ihcc yyav xqpu",
    "alan.dromas@qonto.com": "gfbh alvw fkhc svez",
}

QTF_Fund_name_string = "QTF"
QLF_Fund_name_string = "QLF"
AMUNDI2_Fund_name_string = "AMUNDI2"

QLF_subject = "Lyxor Qonto Fund - Inventaire"
QTF_subject = "QONTO TREASURY - Inventaire"
Amundi_subject = "Amundi Qonto II - Inventaire"
Swap_QTF_subject = "Inventaire swap Qonto Treasury Fund"

dict_mail_fetching = {
    QTF_Fund_name_string: {
        QTF_subject: ["funds@qonto.com", "no-reply-sgssgallery@sgss.socgen.com"],
        Swap_QTF_subject: ["thomas.sionneau@amundi.com"],
    },
    QLF_Fund_name_string: {
        QLF_subject: ["funds@qonto.com", "no-reply-sgssgallery@sgss.socgen.com"]
    },
    AMUNDI2_Fund_name_string: {
        Amundi_subject: ["funds@qonto.com", "no-reply-sgssgallery@sgss.socgen.com"]
    },
}

amundi2_qlf_swap_path = (
    PATH_PROJECT / "output" / "hard_input" / "AQII QLF - Details Basket Tranche.xlsx"
)
path_irs_file = PATH_PROJECT / "output" / "hard_input" / "Funds_charac_IRS_Swap.xlsx"

SNOWFLAKE_DB = os.getenv("SNOWFLAKE_DB", "RAW")
SNOWFLAKE_SANDBOX = os.getenv("SNOWFLAKE_SANDBOX", "SANDBOX")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "qonto.eu-central-1")
# SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT","ra02209.eu-central-1")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "RISK_COMPLIANCE_ENG")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "TEAM_RISK_COMPLIANCE_WH")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE", "RISK_COMPLIANCE_ENG_ROLE")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "")
