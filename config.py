from collections import namedtuple


PORT = 8001  # Local unused port, change if needed
USER = '<databricks-user-email>'  # Email address of the user with access to Databricks workspace
WORKSPACE_DOMAIN = '<databricks-workspace>'  # Databricks workspace domain name (e.g. `adb-xxx.azuredatabricks.net` )
TENANT_ID = "<ad-tenant-id>"
CLIENT_ID = "<app-client-id>"

TOKEN_IMPORT_PATH = f"/Users/{USER}/token"  # Path where the tokens notebook imported to, change as needed
TEST_NOTEBOOK_IMPORT_PATH = f"/Users/{USER}/token_test"

config_dict = {
    "port": PORT,
    "user": USER,
    "workspace": WORKSPACE_DOMAIN,
    "tenant": TENANT_ID,
    "client": CLIENT_ID,
    "token_import_path": TOKEN_IMPORT_PATH,
    "test_import_path": TEST_NOTEBOOK_IMPORT_PATH
}
config = namedtuple("conf", config_dict.keys())(*config_dict.values())