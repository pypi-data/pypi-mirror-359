from typing import Union
from maleo_identity.models.transfers.results.service.user import MaleoIdentityUserServiceResultsTransfers

class MaleoIdentityUserServiceResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserServiceResultsTransfers.MultipleData,
        MaleoIdentityUserServiceResultsTransfers.NoData,
        MaleoIdentityUserServiceResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserServiceResultsTransfers.SingleData,
        MaleoIdentityUserServiceResultsTransfers.NoData,
        MaleoIdentityUserServiceResultsTransfers.Fail
    ]

    CreateOrUpdate = Union[
        MaleoIdentityUserServiceResultsTransfers.SingleData,
        MaleoIdentityUserServiceResultsTransfers.Fail
    ]

    GetSinglePassword = Union[
        MaleoIdentityUserServiceResultsTransfers.SinglePassword,
        MaleoIdentityUserServiceResultsTransfers.Fail
    ]

    Register = Union[
        MaleoIdentityUserServiceResultsTransfers.SingleRegisterData,
        MaleoIdentityUserServiceResultsTransfers.Fail
    ]