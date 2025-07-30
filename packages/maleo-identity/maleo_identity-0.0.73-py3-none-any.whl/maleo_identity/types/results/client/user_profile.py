from typing import Union
from maleo_identity.models.transfers.results.client.user_profile import MaleoIdentityUserProfileClientResultsTransfers

class MaleoIdentityUserProfileClientResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserProfileClientResultsTransfers.MultipleData,
        MaleoIdentityUserProfileClientResultsTransfers.NoData,
        MaleoIdentityUserProfileClientResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserProfileClientResultsTransfers.SingleData,
        MaleoIdentityUserProfileClientResultsTransfers.Fail
    ]

    CreateOrUpdate = Union[
        MaleoIdentityUserProfileClientResultsTransfers.SingleData,
        MaleoIdentityUserProfileClientResultsTransfers.Fail
    ]