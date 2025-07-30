from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.team_recipient import TeamRecipient
    from ..models.user_recipient import UserRecipient


T = TypeVar("T", bound="UpdateSavedSearchPayload")


@_attrs_define
class UpdateSavedSearchPayload:
    """
    Attributes:
        name (str):
        query (str):
        owner (UserRecipient): User recipient
        description (Union[Unset, str]):
        teams (Union[Unset, List['TeamRecipient']]): Teams that the alert will be routed to send notifications
    """

    name: str
    query: str
    owner: "UserRecipient"
    description: Union[Unset, str] = UNSET
    teams: Union[Unset, List["TeamRecipient"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        query = self.query

        owner = self.owner.to_dict()

        description = self.description

        teams: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.teams, Unset):
            teams = []
            for teams_item_data in self.teams:
                teams_item = teams_item_data.to_dict()
                teams.append(teams_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "query": query,
                "owner": owner,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if teams is not UNSET:
            field_dict["teams"] = teams

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.team_recipient import TeamRecipient
        from ..models.user_recipient import UserRecipient

        d = src_dict.copy()
        name = d.pop("name")

        query = d.pop("query")

        owner = UserRecipient.from_dict(d.pop("owner"))

        description = d.pop("description", UNSET)

        teams = []
        _teams = d.pop("teams", UNSET)
        for teams_item_data in _teams or []:
            teams_item = TeamRecipient.from_dict(teams_item_data)

            teams.append(teams_item)

        update_saved_search_payload = cls(
            name=name,
            query=query,
            owner=owner,
            description=description,
            teams=teams,
        )

        update_saved_search_payload.additional_properties = d
        return update_saved_search_payload

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
