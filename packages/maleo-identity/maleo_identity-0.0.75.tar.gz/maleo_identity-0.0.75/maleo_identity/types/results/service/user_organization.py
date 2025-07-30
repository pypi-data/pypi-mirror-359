from typing import Union
from maleo_identity.models.transfers.results.service.user_organization import MaleoIdentityUserOrganizationServiceResultsTransfers

class MaleoIdentityUserOrganizationServiceResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserOrganizationServiceResultsTransfers.MultipleData,
        MaleoIdentityUserOrganizationServiceResultsTransfers.NoData,
        MaleoIdentityUserOrganizationServiceResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserOrganizationServiceResultsTransfers.SingleData,
        MaleoIdentityUserOrganizationServiceResultsTransfers.NoData,
        MaleoIdentityUserOrganizationServiceResultsTransfers.Fail
    ]

    Assign = Union[
        MaleoIdentityUserOrganizationServiceResultsTransfers.SingleData,
        MaleoIdentityUserOrganizationServiceResultsTransfers.Fail
    ]