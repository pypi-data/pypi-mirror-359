from typing import Union
from maleo_identity.models.transfers.results.service.organization import MaleoIdentityOrganizationServiceResultsTransfers

class MaleoIdentityOrganizationServiceResultsTypes:
    GetMultiple = Union[
        MaleoIdentityOrganizationServiceResultsTransfers.MultipleData,
        MaleoIdentityOrganizationServiceResultsTransfers.NoData,
        MaleoIdentityOrganizationServiceResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityOrganizationServiceResultsTransfers.SingleData,
        MaleoIdentityOrganizationServiceResultsTransfers.NoData,
        MaleoIdentityOrganizationServiceResultsTransfers.Fail
    ]

    GetMultipleStructured = Union[
        MaleoIdentityOrganizationServiceResultsTransfers.MultipleStructured,
        MaleoIdentityOrganizationServiceResultsTransfers.NoData,
        MaleoIdentityOrganizationServiceResultsTransfers.Fail
    ]

    GetSingleStructured = Union[
        MaleoIdentityOrganizationServiceResultsTransfers.SingleStructured,
        MaleoIdentityOrganizationServiceResultsTransfers.NoData,
        MaleoIdentityOrganizationServiceResultsTransfers.Fail
    ]

    CreateOrUpdate = Union[
        MaleoIdentityOrganizationServiceResultsTransfers.SingleData,
        MaleoIdentityOrganizationServiceResultsTransfers.Fail
    ]