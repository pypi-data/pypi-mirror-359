from typing import Union
from maleo_identity.models.transfers.results.client.user_system_role import MaleoIdentityUserSystemRoleClientResultsTransfers

class MaleoIdentityUserSystemRoleClientResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserSystemRoleClientResultsTransfers.MultipleData,
        MaleoIdentityUserSystemRoleClientResultsTransfers.NoData,
        MaleoIdentityUserSystemRoleClientResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserSystemRoleClientResultsTransfers.SingleData,
        MaleoIdentityUserSystemRoleClientResultsTransfers.Fail
    ]

    Assign = Union[
        MaleoIdentityUserSystemRoleClientResultsTransfers.SingleData,
        MaleoIdentityUserSystemRoleClientResultsTransfers.Fail
    ]