from typing import Union
from maleo_identity.models.transfers.results.service.organization_registration_code \
    import MaleoIdentityOrganizationRegistrationCodeServiceResultsTransfers

class MaleoIdentityOrganizationRegistrationCodeServiceResultsTypes:
    GetMultiple = Union[
        MaleoIdentityOrganizationRegistrationCodeServiceResultsTransfers.MultipleData,
        MaleoIdentityOrganizationRegistrationCodeServiceResultsTransfers.NoData,
        MaleoIdentityOrganizationRegistrationCodeServiceResultsTransfers.Fail
    ]

    GetSingle = Union[
        MaleoIdentityOrganizationRegistrationCodeServiceResultsTransfers.SingleData,
        MaleoIdentityOrganizationRegistrationCodeServiceResultsTransfers.NoData,
        MaleoIdentityOrganizationRegistrationCodeServiceResultsTransfers.Fail
    ]

    CreateOrUpdate = Union[
        MaleoIdentityOrganizationRegistrationCodeServiceResultsTransfers.SingleData,
        MaleoIdentityOrganizationRegistrationCodeServiceResultsTransfers.Fail
    ]