from typing import Union
from maleo_identity.models.transfers.results.service.user_system_role import MaleoIdentityUserSystemRoleServiceResultsTransfers

class MaleoIdentityUserSystemRoleServiceResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserSystemRoleServiceResultsTransfers.MultipleData,
        MaleoIdentityUserSystemRoleServiceResultsTransfers.NoData,
        MaleoIdentityUserSystemRoleServiceResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserSystemRoleServiceResultsTransfers.SingleData,
        MaleoIdentityUserSystemRoleServiceResultsTransfers.NoData,
        MaleoIdentityUserSystemRoleServiceResultsTransfers.Fail
    ]

    Assign = Union[
        MaleoIdentityUserSystemRoleServiceResultsTransfers.SingleData,
        MaleoIdentityUserSystemRoleServiceResultsTransfers.Fail
    ]