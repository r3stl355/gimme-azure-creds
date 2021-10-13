import click
import webbrowser
from databricks_cli.sdk import ApiClient, SecretService
from config import Config
from auth import AADAuthHandler

@click.command()
@click.option(
    "--workspace", prompt="Workspace URL", 
    help="URL for Azure Databricks workspace (exclude 'https://') e.g. 'adb-1137934926163478.18.azuredatabricks.net'")
@click.option(
    "--tenant", prompt="Azure AD tenant ID", 
    help="ID for your Azure Active Directory tenant, e.g. '9f37a392-f0ae-4280-9796-f1864a10effc'")
@click.option(
    "--secret-scope", prompt="Databricks secret scope", 
    help="""A Databricks-managed (_not_ Azure Key Vault backed) secret scope in which to store the tokens.
    You should ensure that only you have access to this secret scope.""")
@click.option("--secret-key-access", prompt="Secret key for access token", help="Secret key (name) for your Azure AD access token")
@click.option("--secret-key-refresh", prompt="Secret key for refresh token", help="Secret key (name) for your Azure AD refresh token")
def get_token(**kwargs):
    """Obtain a user token from Azure Active Directory and 
    store it as a secret in an Azure Databricks workspace"""

    c = Config(**kwargs)

    auth_handler = AADAuthHandler(c)
    # Get the tokens, upload as a notebook to the workspace and open the workspace in the browser
    try:
        access_token, refresh_token = auth_handler.get_tokens()
    except Exception as e:
        print("Could not obtain an AAD token.")
        raise

    api_client = ApiClient(host=f"https://{c.workspace}", token=access_token)
    secret_service = SecretService(api_client)
    secret_service.put_secret(c.secret_scope, c.secret_key_access, string_value=access_token)
    secret_service.put_secret(c.secret_scope, c.secret_key_refresh, string_value=refresh_token)

    webbrowser.open_new(f'https://{c.workspace}')
