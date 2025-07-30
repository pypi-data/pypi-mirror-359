from typing import Union
from maleo_identity.models.transfers.results.client.user_organization_role import MaleoIdentityUserOrganizationRoleClientResultsTransfers

class MaleoIdentityUserOrganizationRoleClientResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserOrganizationRoleClientResultsTransfers.MultipleData,
        MaleoIdentityUserOrganizationRoleClientResultsTransfers.NoData,
        MaleoIdentityUserOrganizationRoleClientResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserOrganizationRoleClientResultsTransfers.SingleData,
        MaleoIdentityUserOrganizationRoleClientResultsTransfers.Fail
    ]