from __future__ import annotations
from pydantic import Field
from typing import Optional
from maleo_foundation.models.transfers.results.client import BaseClientServiceResultsTransfers
from maleo_identity.models.schemas.user import MaleoIdentityUserSchemas
from maleo_identity.models.transfers.general.user import UserTransfers, PasswordTransfers

class MaleoIdentityUserClientResultsTransfers:
    class Fail(BaseClientServiceResultsTransfers.Fail): pass

    class NoData(BaseClientServiceResultsTransfers.NoData): pass

    class SingleData(BaseClientServiceResultsTransfers.SingleData):
        data:UserTransfers = Field(..., description="Single user data")

    class MultipleData(BaseClientServiceResultsTransfers.PaginatedMultipleData):
        data:list[UserTransfers] = Field(..., description="Multiple users data")

    class SinglePassword(BaseClientServiceResultsTransfers.SingleData):
        data:PasswordTransfers = Field(..., description="Single user password")

    class SingleRegisterData(BaseClientServiceResultsTransfers.SingleData):
        data:UserTransfers = Field(..., description="Single user data")
        metadata:Optional[MaleoIdentityUserSchemas.RegisterResultMetadata] = Field(None, description="Optional metadata")