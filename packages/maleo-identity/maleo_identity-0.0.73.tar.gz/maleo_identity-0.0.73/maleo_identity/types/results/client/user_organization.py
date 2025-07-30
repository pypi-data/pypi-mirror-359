from typing import Union
from maleo_identity.models.transfers.results.client.user_organization import MaleoIdentityUserOrganizationClientResultsTransfers

class MaleoIdentityUserOrganizationClientResultsTypes:
    GetMultiple = Union[
        MaleoIdentityUserOrganizationClientResultsTransfers.MultipleData,
        MaleoIdentityUserOrganizationClientResultsTransfers.NoData,
        MaleoIdentityUserOrganizationClientResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityUserOrganizationClientResultsTransfers.SingleData,
        MaleoIdentityUserOrganizationClientResultsTransfers.Fail
    ]

    Assign = Union[
        MaleoIdentityUserOrganizationClientResultsTransfers.SingleData,
        MaleoIdentityUserOrganizationClientResultsTransfers.Fail
    ]