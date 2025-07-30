from typing import Union
from maleo_identity.models.transfers.results.service.user_organization_role import MaleoIdentityUserOrganizationRoleServiceResultsTransfers

class MaleoIdentityUserOrganizationRoleServiceResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserOrganizationRoleServiceResultsTransfers.MultipleData,
        MaleoIdentityUserOrganizationRoleServiceResultsTransfers.NoData,
        MaleoIdentityUserOrganizationRoleServiceResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserOrganizationRoleServiceResultsTransfers.SingleData,
        MaleoIdentityUserOrganizationRoleServiceResultsTransfers.NoData,
        MaleoIdentityUserOrganizationRoleServiceResultsTransfers.Fail
    ]