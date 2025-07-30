from typing import Union
from maleo_identity.models.transfers.results.client.organization_registration_code \
    import MaleoIdentityOrganizationRegistrationCodeClientResultsTransfers

class MaleoIdentityOrganizationRegistrationCodeClientResultsTypes:
    GetMultiple = Union[
        MaleoIdentityOrganizationRegistrationCodeClientResultsTransfers.MultipleData,
        MaleoIdentityOrganizationRegistrationCodeClientResultsTransfers.NoData,
        MaleoIdentityOrganizationRegistrationCodeClientResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityOrganizationRegistrationCodeClientResultsTransfers.SingleData,
        MaleoIdentityOrganizationRegistrationCodeClientResultsTransfers.Fail
    ]

    Create = Union[
        MaleoIdentityOrganizationRegistrationCodeClientResultsTransfers.SingleData,
        MaleoIdentityOrganizationRegistrationCodeClientResultsTransfers.Fail
    ]