from typing import Union
from maleo_identity.models.transfers.results.service.user_profile import MaleoIdentityUserProfileServiceResultsTransfers

class MaleoIdentityUserProfileServiceResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserProfileServiceResultsTransfers.MultipleData,
        MaleoIdentityUserProfileServiceResultsTransfers.NoData,
        MaleoIdentityUserProfileServiceResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserProfileServiceResultsTransfers.SingleData,
        MaleoIdentityUserProfileServiceResultsTransfers.NoData,
        MaleoIdentityUserProfileServiceResultsTransfers.Fail
    ]

    CreateOrUpdate = Union[
        MaleoIdentityUserProfileServiceResultsTransfers.SingleData,
        MaleoIdentityUserProfileServiceResultsTransfers.Fail
    ]