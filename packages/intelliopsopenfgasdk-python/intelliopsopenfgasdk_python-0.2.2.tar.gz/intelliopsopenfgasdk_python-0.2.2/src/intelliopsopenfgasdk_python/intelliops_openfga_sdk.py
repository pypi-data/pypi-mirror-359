from .models import (
    CreateFgaModel,
    CreateGroupsModel,
    CreateL1L2ObjectsModel,
    CreateDataSourceModel,
    CheckAccessModel,
    CheckMultipleAccessModel,
)
from .http_client import HttpClient
import httpx
from typing import Dict


class IntelliOpsOpenFgaSDK:
    def __init__(self, base_url="http://localhost:3002", headers=None, timeout=10.0):
        """
        Initializes the IntelliOpsOpenFgaSDK with a reusable HttpClient instance.
        Args:
            base_url (str, optional): The base URL for the HttpClient.
            headers (dict, optional): Default headers for the HttpClient.
            timeout (float, optional): Timeout for requests in seconds.
        """
        self.http_client = HttpClient(
            base_url=base_url, headers=headers, timeout=timeout
        )

    def initialize(self, create_fga_model: CreateFgaModel) -> None:
        """
        Initializes the SDK by setting up the HttpClient.
        This method can be extended to perform any additional initialization logic if needed.
        Returns:
            None
        """
        create_datasource_model = CreateDataSourceModel(
            intelliopsTenantUId=create_fga_model.intelliopsTenantUId,
            intelliopsConnectorType=create_fga_model.intelliopsConnectorType,
            datasourceTenantUId=create_fga_model.datasourceTenantUId,
        )
        self.__init_datasource(create_datasource_model)

        self.__init_fga(create_fga_model)

    def _handle_http_error(self, exc):
        status_code = getattr(exc.response, "status_code", None)
        text = getattr(exc.response, "text", str(exc))
        raise RuntimeError(f"HTTP error occurred: {status_code} - {text}") from exc

    def _handle_request_error(self, exc):
        raise RuntimeError(f"Request error occurred: {exc}") from exc

    def __init_datasource(self, create_datasource_model: CreateDataSourceModel) -> None:
        """
        Initializes the datasource for FGA.
        Args:
            create_datasource_model (CreateDataSourceModel): The model containing the necessary parameters.
        Returns:
            None
        Raises:
            httpx.HTTPStatusError: If the response status is not 2xx.
            httpx.RequestError: For network-related errors.
        """
        init_datasource_endpoint = "/auth/sync"
        try:
            response = self.http_client.post(
                init_datasource_endpoint, json=create_datasource_model.model_dump()
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except httpx.RequestError as exc:
            self._handle_request_error(exc)

    async def __async_init_datasource(
        self, create_datasource_model: CreateDataSourceModel
    ) -> None:
        """
        Asynchronously initializes the datasource for FGA.
        """
        init_datasource_endpoint = "/auth/sync"
        try:
            response = await self.http_client.async_post(
                init_datasource_endpoint, json=create_datasource_model.model_dump()
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except httpx.RequestError as exc:
            self._handle_request_error(exc)

    def __init_fga(self, create_fga_model: CreateFgaModel) -> None:
        """
        Creates a new FGA model.
        """
        create_groups_endpoint = "/confluence/create-groups"
        create_l1_l2_objects_endpoint = "/confluence/create-l1-l2-objects"
        try:
            create_groups_model: CreateGroupsModel = CreateGroupsModel(
                intelliopsTenantUId=create_fga_model.intelliopsTenantUId,
                intelliopsUserUId=create_fga_model.intelliopsUserUId,
                intelliopsConnectorUId=create_fga_model.intelliopsConnectorUId,
                accessToken=create_fga_model.accessToken,
                refreshToken=create_fga_model.refreshToken,
            )
            create_groups_model_response = self.http_client.post(
                create_groups_endpoint, json=create_groups_model.model_dump()
            )
            create_groups_model_response.raise_for_status()
            create_l1_l2_objects_model: CreateL1L2ObjectsModel = CreateL1L2ObjectsModel(
                intelliopsUserUId=create_fga_model.intelliopsUserUId,
                intelliopsTenantUId=create_fga_model.intelliopsTenantUId,
                datasourceTenantUId=create_fga_model.datasourceTenantUId,
                intelliopsConnectorUId=create_fga_model.intelliopsConnectorUId,
                accessToken=create_fga_model.accessToken,
                refreshToken=create_fga_model.refreshToken,
            )
            create_l1_l2_objects_model_response = self.http_client.post(
                create_l1_l2_objects_endpoint, json=create_l1_l2_objects_model.model_dump()
            )
            create_l1_l2_objects_model_response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except httpx.RequestError as exc:
            self._handle_request_error(exc)

    async def __async_init_fga(self, create_fga_model: CreateFgaModel) -> None:
        """
        Asynchronously creates a new FGA model.
        """
        create_groups_endpoint = "/confluence/create-groups"
        create_l1_l2_objects_endpoint = "/confluence/create-l1-l2-objects"
        try:
            create_groups_model: CreateGroupsModel = CreateGroupsModel(
                intelliopsTenantUId=create_fga_model.intelliopsTenantUId,
                intelliopsUserUId=create_fga_model.intelliopsUserUId,
                intelliopsConnectorUId=create_fga_model.intelliopsConnectorUId,
                accessToken=create_fga_model.accessToken,
                refreshToken=create_fga_model.refreshToken,
            )
            create_groups_model_response = await self.http_client.async_post(
                create_groups_endpoint, json=create_groups_model.model_dump()
            )
            create_groups_model_response.raise_for_status()
            create_l1_l2_objects_model: CreateL1L2ObjectsModel = CreateL1L2ObjectsModel(
                intelliopsUserUId=create_fga_model.intelliopsUserUId,
                intelliopsTenantUId=create_fga_model.intelliopsTenantUId,
                datasourceTenantUId=create_fga_model.datasourceTenantUId,
                intelliopsConnectorUId=create_fga_model.intelliopsConnectorUId,
                accessToken=create_fga_model.accessToken,
                refreshToken=create_fga_model.refreshToken,
            )
            create_l1_l2_objects_model_response = await self.http_client.async_post(
                create_l1_l2_objects_endpoint, json=create_l1_l2_objects_model.model_dump()
            )
            create_l1_l2_objects_model_response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except httpx.RequestError as exc:
            self._handle_request_error(exc)

    def check_access(self, check_access_model: CheckAccessModel) -> bool:
        """
        Checks access for the user.
        """
        check_access_endpoint = "/access/check"
        try:
            response = self.http_client.post(
                check_access_endpoint,
                json={
                    "intelliopsUserUId": check_access_model.intelliopsUserUId,
                    "objectId": check_access_model.fgaObjectId,
                },
            )
            response.raise_for_status()
            hasAccess = response.json().get("hasAccess", False)
            return hasAccess
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except httpx.RequestError as exc:
            self._handle_request_error(exc)

    async def async_check_access(self, check_access_model: CheckAccessModel) -> bool:
        """
        Asynchronously checks access for the user.
        """
        check_access_endpoint = "/access/check"
        try:
            response = await self.http_client.async_post(
                check_access_endpoint,
                json={
                    "intelliopsUserUId": check_access_model.intelliopsUserUId,
                    "objectId": check_access_model.fgaObjectId,
                },
            )
            response.raise_for_status()
            return response.json().get("hasAccess", False)
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except httpx.RequestError as exc:
            self._handle_request_error(exc)

    def check_multi_access(
        self, check_access_model: CheckMultipleAccessModel
    ) -> Dict[str, bool]:
        """
        Checks access for the user.
        """
        check_multi_access_endpoint = "/access/multi-check"
        try:
            response = self.http_client.post(
                check_multi_access_endpoint,
                json={
                    "intelliopsUserUId": check_access_model.intelliopsUserUId,
                    "objectId": check_access_model.fgaObjectIds,
                },
            )
            response.raise_for_status()
            res = response.json()
            return {
                item["l2object"].split("_")[-1]: item["hasAccess"]
                for item in res["results"]["results"]
            }
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except httpx.RequestError as exc:
            self._handle_request_error(exc)

    async def async_check_multi_access(
        self, check_access_model: CheckMultipleAccessModel
    ) -> Dict[str, bool]:
        """
        Checks access for the user.
        """
        check_multi_access_endpoint = "/access/multi-check"
        try:
            response = await self.http_client.async_post(
                check_multi_access_endpoint,
                json={
                    "intelliopsUserUId": check_access_model.intelliopsUserUId,
                    "objectId": check_access_model.fgaObjectIds,
                },
            )
            response.raise_for_status()
            res = response.json()
            return {
                item["l2object"].split("_")[-1]: item["hasAccess"]
                for item in res["results"]["results"]
            }
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except httpx.RequestError as exc:
            self._handle_request_error(exc)
