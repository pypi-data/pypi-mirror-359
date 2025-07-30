from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Enum, Integer, Date, Text
from maleo_metadata.enums.blood_type import MaleoMetadataBloodTypeEnums
from maleo_metadata.enums.gender import MaleoMetadataGenderEnums
from maleo_identity.db import MaleoIdentityMetadataManager
from maleo_foundation.models.table import DataTable

class UserProfilesMixin:
    #* Foreign Key and Relationship to UsersTable
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_card = Column(name="id_card", type_=String(16))
    leading_title = Column(name="leading_title", type_=String(25))
    first_name = Column(name="first_name", type_=String(50), nullable=False)
    middle_name = Column(name="middle_name", type_=String(50))
    last_name = Column(name="last_name", type_=String(50), nullable=False)
    ending_title = Column(name="ending_title", type_=String(25))
    full_name = Column(name="full_name", type_=String(200), nullable=False)
    birth_place = Column(name="birth_place", type_=String(50))
    birth_date = Column(name="birth_date", type_=Date)
    gender = Column(name="gender", type_=Enum(MaleoMetadataGenderEnums.Gender, name="gender"))
    blood_type = Column(name="blood_type", type_=Enum(MaleoMetadataBloodTypeEnums.BloodType, name="blood_type"))
    avatar_name = Column(name="avatar_name", type_=Text, nullable=False)

class UserProfilesTable(
    UserProfilesMixin,
    DataTable,
    MaleoIdentityMetadataManager.Base
):
    __tablename__ = "user_profiles"
    user = relationship("UsersTable", back_populates="profile")