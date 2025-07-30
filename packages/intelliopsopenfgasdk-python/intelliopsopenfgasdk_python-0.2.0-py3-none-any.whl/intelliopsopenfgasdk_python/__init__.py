from .intelliops_openfga_sdk import IntelliOpsOpenFgaSDK
from .models import (
    CreateFgaModel,
    CreateDataSourceModel,
    CheckAccessModel,
    CheckMultipleAccessModel,
)

__all__ = [
    "IntelliOpsOpenFgaSDK",
    "CreateFgaModel",
    "CreateDataSourceModel",
    "CheckAccessModel",
    "CheckMultipleAccessModel",
]
__version__ = "0.2.0"
__author__ = "IntelliOps"
