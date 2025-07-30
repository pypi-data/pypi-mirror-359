import pytest
from intelliopsopenfgasdk_python.intelliops_openfga_sdk import IntelliOpsOpenFgaSDK
from intelliopsopenfgasdk_python.models import CreateFgaModel, CreateDataSourceModel, CheckAccessModel, CheckMultipleAccessModel
import httpx
import asyncio


class DummyResponse:
    def __init__(self, status_code=200, json_data=None):
        self._status_code = status_code
        self.status_code = status_code  # Add this for compatibility with httpx.Response
        self._json_data = json_data or {}
        self.text = str(json_data)

    def raise_for_status(self):
        if not (200 <= self._status_code < 300):
            raise httpx.HTTPStatusError("error", request=None, response=self)

    def json(self):
        return self._json_data


class DummyHttpClient:
    def __init__(self):
        self.last_post = None

    def post(self, url, json=None):
        self.last_post = (url, json)
        # Simulate different endpoints
        if url == "confluence/create-groups":
            return DummyResponse(200)
        elif url == "confluence/create-l1-l2-objects":
            return DummyResponse(200)
        elif url == "access/check":
            # Return False for a specific l2_object_id to test negative case
            if json and json.get("l2_object_id") == "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_19048045":
                return DummyResponse(200, {"hasAccess": False})
            return DummyResponse(200, {"hasAccess": True})
        return DummyResponse(404)


def test_init_fga_success(monkeypatch):
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyHttpClient()
    model = CreateFgaModel(
        intelliopsUserUId="user",
        intelliopsTenantUId="tenant",
        intelliopsConnectorUId="connector",
        intelliopsConnectorType="Confluence",
        datasourceTenantUId="datasource-tenant",
        accessToken="access-token",
        refreshToken="refresh-token"
    )
    sdk._IntelliOpsOpenFgaSDK__init_fga(model)
    # Should call both endpoints
    assert sdk.http_client.last_post[0] == 'confluence/create-l1-l2-objects'


def test_init_fga_http_error(monkeypatch):
    class ErrorHttpClient(DummyHttpClient):
        def post(self, url, json=None):
            return DummyResponse(400)
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = ErrorHttpClient()
    model = CreateFgaModel(
        intelliopsUserUId="user",
        intelliopsTenantUId="tenant",
        intelliopsConnectorUId="connector",
        intelliopsConnectorType="Confluence",
        datasourceTenantUId="datasource-tenant",
        accessToken="access-token",
        refreshToken="refresh-token"
    )
    with pytest.raises(RuntimeError):
        sdk._IntelliOpsOpenFgaSDK__init_fga(model)


def test_check_access_true():
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyHttpClient()
    model = CheckAccessModel(
        intelliopsUserUId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_5b70c8b80fd0ac05d389f5e9",
        fgaObjectId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_190480451"
    )
    assert sdk.check_access(model) is True


def test_check_access_false():
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyHttpClient()
    model = CheckAccessModel(
        intelliopsUserUId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_5b70c8b80fd0ac05d389f5e9",
        fgaObjectId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_19048045"
    )
    assert sdk.check_access(model) is False


def test_init_datasource_success():
    from intelliopsopenfgasdk_python.models import CreateDataSourceModel
    class DummyHttpClientDs(DummyHttpClient):
        def post(self, url, json=None):
            assert url == "auth/sync"
            return DummyResponse(200)
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyHttpClientDs()
    model = CreateDataSourceModel(
        intelliopsTenantUId="tenant",
        intelliopsConnectorType="Confluence",
        datasourceTenantUId="datasource-tenant"
    )
    sdk._IntelliOpsOpenFgaSDK__init_datasource(model)


def test_init_datasource_http_error():
    from intelliopsopenfgasdk_python.models import CreateDataSourceModel
    class ErrorHttpClient(DummyHttpClient):
        def post(self, url, json=None):
            return DummyResponse(400)
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = ErrorHttpClient()
    model = CreateDataSourceModel(
        intelliopsTenantUId="tenant",
        intelliopsConnectorType="Confluence",
        datasourceTenantUId="datasource-tenant"
    )
    with pytest.raises(RuntimeError):
        sdk._IntelliOpsOpenFgaSDK__init_datasource(model)


def test_initialize_calls_both(monkeypatch):
    class TrackHttpClient(DummyHttpClient):
        def __init__(self):
            super().__init__()
            self.calls = []
        def post(self, url, json=None):
            self.calls.append(url)
            return DummyResponse(200)
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = TrackHttpClient()
    model = CreateFgaModel(
        intelliopsUserUId="user",
        intelliopsTenantUId="tenant",
        intelliopsConnectorUId="connector",
        intelliopsConnectorType="Confluence",
        datasourceTenantUId="datasource-tenant",
        accessToken="access-token",
        refreshToken="refresh-token"
    )
    sdk.initialize(model)
    assert "auth/sync" in sdk.http_client.calls
    assert "confluence/create-groups" in sdk.http_client.calls
    assert "confluence/create-l1-l2-objects" in sdk.http_client.calls


@pytest.mark.asyncio
def test_async_init_datasource_success():
    from intelliopsopenfgasdk_python.models import CreateDataSourceModel
    class DummyAsyncHttpClient(DummyHttpClient):
        async def async_post(self, url, json=None):
            assert url == "auth/sync"
            return DummyResponse(200)
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyAsyncHttpClient()
    model = CreateDataSourceModel(
        intelliopsTenantUId="tenant",
        intelliopsConnectorType="Confluence",
        datasourceTenantUId="datasource-tenant"
    )
    asyncio.run(sdk._IntelliOpsOpenFgaSDK__async_init_datasource(model))


@pytest.mark.asyncio
def test_async_init_fga_success():
    class DummyAsyncHttpClient(DummyHttpClient):
        async def async_post(self, url, json=None):
            return DummyResponse(200)
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyAsyncHttpClient()
    model = CreateFgaModel(
        intelliopsUserUId="user",
        intelliopsTenantUId="tenant",
        intelliopsConnectorUId="connector",
        intelliopsConnectorType="Confluence",
        datasourceTenantUId="datasource-tenant",
        accessToken="access-token",
        refreshToken="refresh-token"
    )
    asyncio.run(sdk._IntelliOpsOpenFgaSDK__async_init_fga(model))


@pytest.mark.asyncio
def test_async_check_access_true():
    class DummyAsyncHttpClient(DummyHttpClient):
        async def async_post(self, url, json=None):
            return DummyResponse(200, {"hasAccess": True})
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyAsyncHttpClient()
    model = CheckAccessModel(
        intelliopsUserUId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_5b70c8b80fd0ac05d389f5e9",
        fgaObjectId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_190480451"
    )
    result = asyncio.run(sdk.async_check_access(model))
    assert result is True


@pytest.mark.asyncio
def test_async_check_access_false():
    class DummyAsyncHttpClient(DummyHttpClient):
        async def async_post(self, url, json=None):
            return DummyResponse(200, {"hasAccess": False})
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyAsyncHttpClient()
    model = CheckAccessModel(
        intelliopsUserUId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_5b70c8b80fd0ac05d389f5e9",
        fgaObjectId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_19048045"
    )
    result = asyncio.run(sdk.async_check_access(model))
    assert result is False


def test_check_multi_access():
    class DummyHttpClientMulti(DummyHttpClient):
        def post(self, url, json=None):
            if url == "access/multi-check":
                return DummyResponse(200, {
                    "results": {
                        "results": [
                            {"l2object": "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_550568177", "hasAccess": True},
                            {"l2object": "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_669876453", "hasAccess": False},
                            {"l2object": "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_190480451", "hasAccess": True}
                        ]
                    }
                })
            return super().post(url, json)
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyHttpClientMulti()
    model = CheckMultipleAccessModel(
        intelliopsUserUId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_5b70c8b80fd0ac05d389f5e9",
        fgaObjectIds=[
            "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_550568177",
            "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_669876453",
            "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_190480451"
        ]
    )
    result = sdk.check_multi_access(model)
    assert result == {
        "550568177": True,
        "669876453": False,
        "190480451": True
    }


@pytest.mark.asyncio
def test_async_check_multi_access():
    class DummyAsyncHttpClientMulti(DummyHttpClient):
        async def async_post(self, url, json=None):
            if url == "access/multi-check":
                return DummyResponse(200, {
                    "results": {
                        "results": [
                            {"l2object": "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_550568177", "hasAccess": True},
                            {"l2object": "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_669876453", "hasAccess": False},
                            {"l2object": "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_190480451", "hasAccess": True}
                        ]
                    }
                })
            return await super().post(url, json)
    sdk = IntelliOpsOpenFgaSDK()
    sdk.http_client = DummyAsyncHttpClientMulti()
    model = CheckMultipleAccessModel(
        intelliopsUserUId="t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_5b70c8b80fd0ac05d389f5e9",
        fgaObjectIds=[
            "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_550568177",
            "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_669876453",
            "t417ce8a_Confluence_e4448be1-8022-43a2-b234-e467842aac60_190480451"
        ]
    )
    result = asyncio.run(sdk.async_check_multi_access(model))
    assert result == {
        "550568177": True,
        "669876453": False,
        "190480451": True
    }
