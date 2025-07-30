from typing import Union
from maleo_identity.models.transfers.results.service.organization_role import MaleoIdentityOrganizationRoleServiceResultsTransfers

class MaleoIdentityOrganizationRoleServiceResultsTypes:
    GetMultiple = Union[
        MaleoIdentityOrganizationRoleServiceResultsTransfers.MultipleData,
        MaleoIdentityOrganizationRoleServiceResultsTransfers.NoData,
        MaleoIdentityOrganizationRoleServiceResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityOrganizationRoleServiceResultsTransfers.SingleData,
        MaleoIdentityOrganizationRoleServiceResultsTransfers.NoData,
        MaleoIdentityOrganizationRoleServiceResultsTransfers.Fail
    ]