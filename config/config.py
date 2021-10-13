from dataclasses import dataclass

@dataclass
class Config:
    workspace: str
    tenant: str
    secret_scope: str
    secret_key_access: str
    secret_key_refresh: str
    client: str = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
