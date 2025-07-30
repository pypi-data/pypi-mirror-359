from .intelliops_openfga_sdk import IntelliOpsOpenFgaSDK
from .models import (
    CreateFgaModel,
    CreateDataSourceModel,
    CheckAccessModel,
    CheckMultipleAccessModel,
    FgaObjectModel,
    FgaObjectsModel
)

__all__ = [
    "IntelliOpsOpenFgaSDK",
    "CreateFgaModel",
    "CreateDataSourceModel",
    "CheckAccessModel",
    "CheckMultipleAccessModel",
    "FgaObjectModel",
    "FgaObjectsModel"
]
__version__ = "0.2.7"
__author__ = "IntelliOps"
