from typing import Union
from maleo_identity.models.transfers.results.client.organization import MaleoIdentityOrganizationClientResultsTransfers

class MaleoIdentityOrganizationClientResultsTypes:
    GetMultiple = Union[
        MaleoIdentityOrganizationClientResultsTransfers.MultipleData,
        MaleoIdentityOrganizationClientResultsTransfers.NoData,
        MaleoIdentityOrganizationClientResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityOrganizationClientResultsTransfers.SingleData,
        MaleoIdentityOrganizationClientResultsTransfers.Fail
    ]

    GetMultipleStructured = Union[
        MaleoIdentityOrganizationClientResultsTransfers.MultipleStructured,
        MaleoIdentityOrganizationClientResultsTransfers.NoData,
        MaleoIdentityOrganizationClientResultsTransfers.Fail
    ]

    GetSingleStructured = Union[
        MaleoIdentityOrganizationClientResultsTransfers.SingleStructured,
        MaleoIdentityOrganizationClientResultsTransfers.Fail
    ]

    CreateOrUpdate = Union[
        MaleoIdentityOrganizationClientResultsTransfers.SingleData,
        MaleoIdentityOrganizationClientResultsTransfers.Fail
    ]