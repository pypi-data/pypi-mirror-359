import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, field_serializer

from mmisp.api_schemas.organisations import Organisation
from mmisp.api_schemas.responses.standard_status_response import StandardStatusResponse


class SharingGroup(BaseModel):
    id: int
    name: str
    releasability: str
    description: str
    uuid: str
    organisation_uuid: str
    org_id: int
    sync_user_id: int
    active: bool
    created: datetime
    modified: datetime
    local: bool
    roaming: bool

    @field_serializer("created", "modified")
    def serialize_timestamp(self: Self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")


#    org_count: int = 0


class MinimalSharingGroup(BaseModel):
    id: int
    name: str
    uuid: str


class ShortSharingGroup(BaseModel):
    id: int
    name: str
    releasability: str
    description: str
    uuid: str
    active: bool
    local: bool
    roaming: bool

    org_count: int = 0


class ShortOrganisation(BaseModel):
    id: int
    name: str
    uuid: uuid.UUID


class SharingGroupServer(BaseModel):
    id: int
    sharing_group_id: int
    server_id: int
    all_orgs: bool


class SharingGroupOrg(BaseModel):
    id: int
    sharing_group_id: int
    org_id: int
    extend: bool


class SharingGroupOrgWithOrganisation(SharingGroupOrg):
    Organisation: ShortOrganisation


class EventSharingGroupResponse(SharingGroup):
    Organisation: ShortOrganisation
    SharingGroupOrg: list[SharingGroupOrgWithOrganisation]
    SharingGroupServer: list


class GetAllSharingGroupsResponseResponseItemSharingGroup(BaseModel):
    id: int
    uuid: str
    name: str
    description: str
    releasability: str
    local: bool
    active: bool
    roaming: bool
    org_count: int


class DeleteSharingGroupLegacyResponse(StandardStatusResponse):
    id: int


class ViewUpdateSharingGroupLegacyResponseServerInfo(BaseModel):
    id: int
    name: str
    url: str


class ViewUpdateSharingGroupLegacyResponseSharingGroupServerItem(BaseModel):
    id: int
    sharing_group_id: int
    server_id: int
    all_orgs: bool
    Server: ViewUpdateSharingGroupLegacyResponseServerInfo


class SharingGroupOrgOrganisationIndexInfo(BaseModel):
    id: int
    uuid: str
    name: str


class ViewUpdateSharingGroupLegacyResponseOrganisationInfo(SharingGroupOrgOrganisationIndexInfo):
    local: bool


class ViewUpdateSharingGroupLegacyResponseSharingGroupOrgItem(BaseModel):
    id: int
    sharing_group_id: int
    org_id: int
    extend: bool
    Organisation: ViewUpdateSharingGroupLegacyResponseOrganisationInfo


class SharingGroupOrgIndexItem(BaseModel):
    id: int
    sharing_group_id: int
    org_id: int
    extend: bool
    Organisation: SharingGroupOrgOrganisationIndexInfo


class SharingGroupResponse(BaseModel):
    editable: bool | None = None
    deletable: bool | None = None

    SharingGroup: ShortSharingGroup
    Organisation: ShortOrganisation
    SharingGroupOrg: list[ViewUpdateSharingGroupLegacyResponseSharingGroupOrgItem]
    SharingGroupServer: list[ViewUpdateSharingGroupLegacyResponseSharingGroupServerItem]


class SharingGroupIndexResponse(BaseModel):
    editable: bool | None = None
    deletable: bool | None = None

    SharingGroup: ShortSharingGroup
    Organisation: ShortOrganisation
    SharingGroupOrg: list[SharingGroupOrgIndexItem]
    SharingGroupServer: list[ViewUpdateSharingGroupLegacyResponseSharingGroupServerItem]


class SingleSharingGroupResponse(BaseModel):
    SharingGroup: SharingGroup
    Organisation: Organisation
    SharingGroupOrg: list[ViewUpdateSharingGroupLegacyResponseSharingGroupOrgItem]
    SharingGroupServer: list[ViewUpdateSharingGroupLegacyResponseSharingGroupServerItem]


class ViewUpdateSharingGroupLegacyResponse(SharingGroupResponse):
    pass


class GetSharingGroupsIndex(BaseModel):
    response: list[SharingGroupIndexResponse]


class UpdateSharingGroupLegacyBody(BaseModel):
    id: int | None = None
    """attribute will be ignored"""
    uuid: str | None = Field(default=None, max_length=36)
    """attribute will be ignored"""
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=65535)
    releasability: str | None = Field(default=None, max_length=65535)
    local: bool | None = None
    active: bool | None = None
    org_count: int | None = None
    """attribute will be ignored"""
    organisation_uuid: str | None = Field(default=None, max_length=36)
    """attribute will be ignored"""
    org_id: int | None = None
    """attribute will be ignored"""
    sync_user_id: int | None = None
    """attribute will be ignored"""
    created: datetime | None = None
    """attribute will be ignored"""
    modified: datetime | None = None
    """attribute will be ignored"""
    roaming: bool | None = None

    @field_serializer("created", "modified")
    def serialize_timestamp(self: Self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")


class UpdateSharingGroupBody(BaseModel):
    name: str = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=65535)
    releasability: str = Field(default=None, max_length=65535)
    active: bool | None = None
    roaming: bool | None = None
    local: bool | None = None


class GetSharingGroupInfoResponseServerInfo(BaseModel):
    id: int
    name: str
    url: str


class GetSharingGroupInfoResponseSharingGroupServerItem(BaseModel):
    id: int
    sharing_group_id: int
    server_id: int
    all_orgs: bool
    Server: GetSharingGroupInfoResponseServerInfo


class GetSharingGroupInfoResponseOrganisationInfo(BaseModel):
    id: int
    uuid: str
    name: str
    local: bool


class GetSharingGroupInfoResponseSharingGroupOrgItem(BaseModel):
    id: int
    sharing_group_id: int
    org_id: int
    extend: bool
    Organisation: GetSharingGroupInfoResponseOrganisationInfo


class GetSharingGroupInfoResponseSharingGroupInfo(SharingGroup):
    org_count: int


class GetAllSharingGroupsResponseOrganisationInfo(BaseModel):
    id: int
    uuid: str
    name: str


class GetSharingGroupInfoResponse(BaseModel):
    SharingGroup: GetSharingGroupInfoResponseSharingGroupInfo
    Organisation: Organisation
    SharingGroupOrg: list[GetSharingGroupInfoResponseSharingGroupOrgItem]
    SharingGroupServer: list[GetSharingGroupInfoResponseSharingGroupServerItem]


class GetAllSharingGroupsResponseResponseItemSharingGroupOrgItem(BaseModel):
    id: int
    sharing_group_id: int
    org_id: int
    extend: bool
    Organisation: GetAllSharingGroupsResponseOrganisationInfo


class GetAllSharingGroupsResponseResponseItemSharingGroupServerItemServer(BaseModel):
    id: int
    name: str
    url: str


class GetAllSharingGroupsResponseResponseItemSharingGroupServerItem(BaseModel):
    server_id: int
    sharing_group_id: int
    all_orgs: bool
    Server: GetAllSharingGroupsResponseResponseItemSharingGroupServerItemServer


class GetAllSharingGroupsResponseResponseItem(BaseModel):
    SharingGroup: GetAllSharingGroupsResponseResponseItemSharingGroup
    Organisation: GetAllSharingGroupsResponseOrganisationInfo
    SharingGroupOrg: list[GetAllSharingGroupsResponseResponseItemSharingGroupOrgItem]
    SharingGroupServer: list[GetAllSharingGroupsResponseResponseItemSharingGroupServerItem]
    editable: bool
    deletable: bool


class GetAllSharingGroupsResponse(BaseModel):
    response: list[GetAllSharingGroupsResponseResponseItem]


class CreateSharingGroupLegacyResponseOrganisationInfo(BaseModel):
    id: int
    name: str
    uuid: str


class CreateSharingGroupLegacyResponse(BaseModel):
    SharingGroup: SharingGroup
    Organisation: CreateSharingGroupLegacyResponseOrganisationInfo
    SharingGroupOrg: list[SharingGroupOrg]
    SharingGroupServer: list[SharingGroupServer]


class CreateSharingGroupLegacyBody(BaseModel):
    uuid: str | None = None
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=65535)
    releasability: str | None = Field(default=None, max_length=65535)
    local: bool | None = None
    active: bool | None = None
    org_count: int | None = None
    """attribute will be ignored"""
    organisation_uuid: str | None = Field(default=None, max_length=36)
    org_id: int | None = Field(default=None)
    sync_user_id: int | None = Field(default=None)
    """attribute will be ignored"""
    created: datetime | None = None
    """attribute will be ignored"""
    modified: datetime | None = None
    """attribute will be ignored"""
    roaming: bool | None = None

    @field_serializer("created", "modified")
    def serialize_timestamp(self: Self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")


class CreateSharingGroupBody(BaseModel):
    uuid: str | None = None
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=65535)
    releasability: str = Field(max_length=65535)
    organisation_uuid: str | None = Field(default=None, max_length=36)
    active: bool | None = None
    roaming: bool | None = None
    local: bool | None = None


class AddServerToSharingGroupLegacyBody(BaseModel):
    all_orgs: bool | None = None


class AddServerToSharingGroupBody(BaseModel):
    serverId: int
    all_orgs: bool | None = None


class AddOrgToSharingGroupLegacyBody(BaseModel):
    extend: bool | None = None


class AddOrgToSharingGroupBody(BaseModel):
    organisationId: int
    extend: bool | None = None
