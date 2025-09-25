import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def _qt_offscreen_env():
    # Allow PyQt5 to initialize without a display
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    # Ensure project root is importable
    import sys, pathlib
    root = str(pathlib.Path(__file__).resolve().parents[1])
    if root not in sys.path:
        sys.path.insert(0, root)
    # Provide lightweight stubs for Google API libs if not installed
    try:
        import googleapiclient  # noqa: F401
        import google_auth_oauthlib  # noqa: F401
        import google  # noqa: F401
    except Exception:
        import sys
        import types
        google_pkg = types.ModuleType("google")
        sys.modules.setdefault("google", google_pkg)

        # googleapiclient stubs
        ga = types.ModuleType("googleapiclient")
        discovery = types.ModuleType("googleapiclient.discovery")
        errors = types.ModuleType("googleapiclient.errors")
        http = types.ModuleType("googleapiclient.http")

        def _build(*args, **kwargs):
            class _Svc:
                def videos(self):
                    raise RuntimeError("stub")
            return _Svc()

        class _HttpError(Exception):
            pass

        class _MediaFileUpload:
            def __init__(self, *a, **kw):
                pass

        discovery.build = _build
        errors.HttpError = _HttpError
        http.MediaFileUpload = _MediaFileUpload

        sys.modules["googleapiclient"] = ga
        sys.modules["googleapiclient.discovery"] = discovery
        sys.modules["googleapiclient.errors"] = errors
        sys.modules["googleapiclient.http"] = http

        # google.oauth2.credentials stub
        oauth2 = types.ModuleType("google.oauth2")
        credentials = types.ModuleType("google.oauth2.credentials")

        class _Creds:
            def __init__(self, *a, **k):
                pass

            @staticmethod
            def from_authorized_user_file(*a, **k):
                return _Creds()

            def to_json(self):
                return "{}"

        credentials.Credentials = _Creds
        sys.modules["google.oauth2"] = oauth2
        sys.modules["google.oauth2.credentials"] = credentials

        # google_auth_oauthlib.flow stub
        gflow_root = types.ModuleType("google_auth_oauthlib")
        gflow = types.ModuleType("google_auth_oauthlib.flow")

        class _InstalledAppFlow:
            @classmethod
            def from_client_secrets_file(cls, *a, **k):
                return cls()

            def run_local_server(self, *a, **k):
                return _Creds()

        gflow.InstalledAppFlow = _InstalledAppFlow
        sys.modules["google_auth_oauthlib"] = gflow_root
        sys.modules["google_auth_oauthlib.flow"] = gflow

        # google.auth.transport.requests.Request stub
        gauth = types.ModuleType("google.auth")
        transport = types.ModuleType("google.auth.transport")
        requests = types.ModuleType("google.auth.transport.requests")

        class _Request:
            pass

        requests.Request = _Request
        sys.modules["google.auth"] = gauth
        sys.modules["google.auth.transport"] = transport
        sys.modules["google.auth.transport.requests"] = requests
    yield


@pytest.fixture(scope="session")
def qapp():
    try:
        from PyQt5.QtWidgets import QApplication
    except Exception as e:
        pytest.skip(f"PyQt5 not available: {e}")
    app = QApplication.instance() or QApplication([])
    yield app
    # Do not quit the global app; let pytest exit handle it
