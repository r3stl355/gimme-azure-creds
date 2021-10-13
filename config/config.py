from dataclasses import dataclass

@dataclass
class Config:
    workspace: str
    tenant: str
    secret_scope: str
    secret_key_access: str
    secret_key_refresh: str
    client: str = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
    # port: int = 8001

# config = Config(
#     workspace="adb-1137934926163478.18.azuredatabricks.net/?o=1137934926163478",
#     tenant="9f37a392-f0ae-4280-9796-f1864a10effc",
#     secret_scope="stuart",
#     secret_key_access="aad_access_token",
#     secret_key_refresh="aad_refresh_token"
#     )