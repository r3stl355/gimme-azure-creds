import time
import random
import socket
import webbrowser
from adal import AuthenticationContext
from .server import EventSink, ServerThread


class AADAuthHandler:
    def __init__(self, config):
        self.config = config
        self._port = None
        self.RESOURCE_ID = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"  # Azure Databricks Resource ID
        self.REDIRECT_URI = f"http://localhost:{self.PORT}"
        self.STATE = random.randint(10000, 90000)

    @property
    def PORT(self):
        if not self._port:
            s = socket.socket()
            s.bind(('', 0))
            self._port = s.getsockname()[1]
        return self._port

    def get_authorization_code(self):

        notifier = EventSink()
        t = ServerThread(port=self.PORT, notifier=notifier)
        t.start()

        auth_uri = f'https://login.windows.net/{self.config.tenant}/oauth2/authorize?response_type=code&client_id={self.config.client}' + \
                f'&redirect_uri={self.REDIRECT_URI}&state={self.STATE}&resource={self.RESOURCE_ID}'
        webbrowser.open_new(auth_uri)
        try:
            while not notifier.changed:
                time.sleep(3)
        finally:
            t.join()

        return notifier.message


    def get_tokens(self):
        authority = f"https://login.microsoftonline.com/{self.config.tenant}"
        context = AuthenticationContext(authority)
        auth_code = self.get_authorization_code()
        response = context.acquire_token_with_authorization_code(auth_code, self.REDIRECT_URI, self.RESOURCE_ID, self.config.client)

        return response['accessToken'], response['refreshToken']