from pydantic import BaseModel, Field
from typing import Optional, Dict


class CreateFgaModel(BaseModel):
    intelliopsUserUId: str = Field(..., description="User UId")
    intelliopsTenantUId: str = Field(..., description="Tenant UId")
    intelliopsConnectorUId: str = Field(..., description="Connector UId")
    intelliopsConnectorType: str = Field(..., description="Type of connector")
    datasourceTenantUId: str = Field(..., description="Datasource Tenant UId")
    accessToken: str = Field(..., description="Access Token")
    refreshToken: str = Field(..., description="Refresh Token")


class CreateGroupsModel(BaseModel):
    intelliopsUserUId: str = Field(..., description="User UId")
    intelliopsTenantUId: str = Field(..., description="Tenant UId")
    intelliopsConnectorUId: str = Field(..., description="Connector UId")
    accessToken: str = Field(..., description="Access Token")
    refreshToken: str = Field(..., description="Refresh Token")


class CreateL1L2ObjectsModel(BaseModel):
    intelliopsUserUId: str = Field(..., description="User UId")
    intelliopsTenantUId: str = Field(..., description="Tenant UId")
    datasourceTenantUId: str = Field(..., description="Datasource Tenant UId")
    intelliopsConnectorUId: str = Field(..., description="Connector UId")
    accessToken: str = Field(..., description="Access Token")
    refreshToken: str = Field(..., description="Refresh Token")


class CreateDataSourceModel(BaseModel):
    intelliopsTenantUId: str = Field(..., description="Tenant UId")
    intelliopsConnectorType: str = Field(..., description="Type of connector")
    datasourceTenantUId: str = Field(..., description="Datasource Tenant UId")


class CheckAccessModel(BaseModel):
    user_uid: str = Field(..., description="User UId")
    object_id: str = Field(..., description="L2 Object ID")


class CheckMultipleAccessModel(BaseModel):
    user_uid: str = Field(..., description="User UId")
    object_ids: list[str] = Field(..., description="List of Data Object IDs")
