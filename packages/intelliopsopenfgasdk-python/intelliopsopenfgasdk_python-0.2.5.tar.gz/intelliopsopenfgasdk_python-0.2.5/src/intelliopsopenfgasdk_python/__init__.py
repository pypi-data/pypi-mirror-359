from .intelliops_openfga_sdk import IntelliOpsOpenFgaSDK
from .models import (
    CreateFgaModel,
    CreateDataSourceModel,
    CheckAccessModel,
    CheckMultipleAccessModel,
    FgaObjectModel
)

__all__ = [
    "IntelliOpsOpenFgaSDK",
    "CreateFgaModel",
    "CreateDataSourceModel",
    "CheckAccessModel",
    "CheckMultipleAccessModel",
    "FgaObjectModel"
]
__version__ = "0.2.5"
__author__ = "IntelliOps"
