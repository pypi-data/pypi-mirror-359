from typing import Union
from maleo_identity.models.transfers.results.client.organization_role import MaleoIdentityOrganizationRoleClientResultsTransfers

class MaleoIdentityOrganizationRoleClientResultsTypes:
    GetMultiple = Union[
        MaleoIdentityOrganizationRoleClientResultsTransfers.MultipleData,
        MaleoIdentityOrganizationRoleClientResultsTransfers.NoData,
        MaleoIdentityOrganizationRoleClientResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityOrganizationRoleClientResultsTransfers.SingleData,
        MaleoIdentityOrganizationRoleClientResultsTransfers.Fail
    ]