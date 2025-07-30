import ssl
import socket
import urllib3
from urllib3.connection import HTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool
from requests.adapters import HTTPAdapter
from requests.sessions import Session as RequestsSession


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SNIHTTPSConnection(HTTPSConnection):
    def __init__(self, *args, sni:str=None, no_sni:bool=False, **kwargs):
        self._sni = sni
        self._no_sni = no_sni
        kwargs.pop("scheme", None)
        kwargs.pop("strict", None)
        super().__init__(*args, **kwargs)

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout, self.source_address)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        if self._no_sni == True:
            server_hostname = None
        else:
            server_hostname = self.host if self._sni is None else self._sni
        self.sock = context.wrap_socket(sock, server_hostname=server_hostname)

class SNIHTTPSConnectionPool(HTTPSConnectionPool):
    def __init__(self, *args, sni:str=None, no_sni:bool=False, **kwargs):
        self._sni = sni
        self._no_sni = no_sni
        super().__init__(*args, **kwargs)

    def _new_conn(self):
        self.num_connections += 1
        return SNIHTTPSConnection(host=self.host, port=self.port, timeout=self.timeout, sni=self._sni, no_sni=self._no_sni)

class SNIAdapter(HTTPAdapter):
    def __init__(self, sni:str=None, no_sni:bool=False, **kwargs):
        self._sni = sni
        self._no_sni = no_sni
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        sni = self._sni
        no_sni = self._no_sni

        class CustomHTTPSConnection(SNIHTTPSConnection):
            def __init__(self, *args, **conn_kwargs):
                super().__init__(*args, sni=sni, no_sni=no_sni, **conn_kwargs)  # Use captured sni

        class CustomHTTPSConnectionPool(HTTPSConnectionPool):
            ConnectionCls = CustomHTTPSConnection

        class CustomPoolManager(urllib3.poolmanager.PoolManager):
            def _new_pool(self, scheme, host, port, request_context=None):
                if scheme == "https":
                    request_context = request_context or {}
                    request_context = request_context.copy()
                    request_context.pop("host", None)
                    request_context.pop("port", None)
                    return CustomHTTPSConnectionPool(host=host, port=port, **request_context)
                return super()._new_pool(scheme, host, port, request_context)

        self.poolmanager = CustomPoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            **pool_kwargs,
        )


class Session:
    def __init__(self, sni:str=None, no_sni:bool=False):
        self._session = RequestsSession()
        self._sni = sni
        self._no_sni = no_sni
        sni_adapter = SNIAdapter(sni=sni, no_sni=no_sni)
        self._session.mount('https://', sni_adapter)

    def request(self, method, url, **kwargs):
        return self._session.request(method, url, **kwargs)

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request('PATCH', url, **kwargs)

    def head(self, url, **kwargs):
        return self.request('HEAD', url, **kwargs)

    def options(self, url, **kwargs):
        return self.request('OPTIONS', url, **kwargs)

    def close(self):
        return self._session.close()


def get(url, sni:str=None, no_sni:bool=False, **kwargs):
    session = Session(sni=sni, no_sni=no_sni)
    try:
        return session.get(url, **kwargs)
    finally:
        session.close()

def post(url, sni:str=None, no_sni:bool=False, **kwargs):
    session = Session(sni=sni, no_sni=no_sni)
    try:
        return session.post(url, **kwargs)
    finally:
        session.close()

def put(url, sni:str=None, no_sni:bool=False, **kwargs):
    session = Session(sni=sni, no_sni=no_sni)
    try:
        return session.put(url, **kwargs)
    finally:
        session.close()

def delete(url, sni:str=None, no_sni:bool=False, **kwargs):
    session = Session(sni=sni, no_sni=no_sni)
    try:
        return session.delete(url, **kwargs)
    finally:
        session.close()

def patch(url, sni:str=None, no_sni:bool=False, **kwargs):
    session = Session(sni=sni, no_sni=no_sni)
    try:
        return session.patch(url, **kwargs)
    finally:
        session.close()

def head(url, sni:str=None, no_sni:bool=False, **kwargs):
    session = Session(sni=sni, no_sni=no_sni)
    try:
        return session.head(url, **kwargs)
    finally:
        session.close()

def options(url, sni:str=None, no_sni:bool=False, **kwargs):
    session = Session(sni=sni, no_sni=no_sni)
    try:
        return session.options(url, **kwargs)
    finally:
        session.close()