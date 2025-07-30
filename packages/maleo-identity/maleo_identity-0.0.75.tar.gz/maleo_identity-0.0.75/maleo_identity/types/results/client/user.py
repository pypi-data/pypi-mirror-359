from typing import Union
from maleo_identity.models.transfers.results.client.user import MaleoIdentityUserClientResultsTransfers

class MaleoIdentityUserClientResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserClientResultsTransfers.MultipleData,
        MaleoIdentityUserClientResultsTransfers.NoData,
        MaleoIdentityUserClientResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserClientResultsTransfers.SingleData,
        MaleoIdentityUserClientResultsTransfers.Fail
    ]

    CreateOrUpdate = Union[
        MaleoIdentityUserClientResultsTransfers.SingleData,
        MaleoIdentityUserClientResultsTransfers.Fail
    ]

    GetSinglePassword = Union[
        MaleoIdentityUserClientResultsTransfers.SinglePassword,
        MaleoIdentityUserClientResultsTransfers.Fail
    ]

    Register = Union[
        MaleoIdentityUserClientResultsTransfers.SingleRegisterData,
        MaleoIdentityUserClientResultsTransfers.Fail
    ]