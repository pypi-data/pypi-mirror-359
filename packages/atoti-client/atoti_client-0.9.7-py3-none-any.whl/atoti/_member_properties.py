from collections.abc import Mapping, Set as AbstractSet
from typing import Final, TypeAlias, final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableMapping
from ._graphql_client import (
    CreateMemberPropertyInput,
    DeleteMemberPropertyInput,
    DeleteStatus,
    GraphQLField,
    Mutation,
)
from ._identification import (
    ColumnIdentifier,
    CubeIdentifier,
    Identifiable,
    LevelIdentifier,
    identify,
)
from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, get_type_adapter


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class _DeleteMemberPropertyOutput:
    status: DeleteStatus


_DeleteMemberPropertiesOutput: TypeAlias = Mapping[str, _DeleteMemberPropertyOutput]


@final
class MemberProperties(DelegatingMutableMapping[str, Identifiable[ColumnIdentifier]]):
    def __init__(
        self,
        level_identifier: LevelIdentifier,
        /,
        *,
        client: Client,
        cube_identifier: CubeIdentifier,
    ):
        self._client: Final = client
        self._cube_identifier: Final = cube_identifier
        self._level_identifier: Final = level_identifier

    @override
    def _get_delegate(
        self,
        *,
        key: str | None,
    ) -> Mapping[str, Identifiable[ColumnIdentifier]]:
        graphql_client = self._client._require_graphql_client()
        if key is None:
            get_properties_output = graphql_client.get_member_properties(
                cube_name=self._cube_identifier.cube_name,
                dimension_name=self._level_identifier.hierarchy_identifier.dimension_identifier.dimension_name,
                hierarchy_name=self._level_identifier.hierarchy_identifier.hierarchy_name,
                level_name=self._level_identifier.level_name,
            )

            return {
                member_property.name: ColumnIdentifier._from_graphql(
                    member_property.column
                )
                for member_property in get_properties_output.data_model.cube.dimension.hierarchy.level.member_properties
            }

        get_property_output = graphql_client.find_member_property(
            cube_name=self._cube_identifier.cube_name,
            dimension_name=self._level_identifier.hierarchy_identifier.dimension_identifier.dimension_name,
            hierarchy_name=self._level_identifier.hierarchy_identifier.hierarchy_name,
            level_name=self._level_identifier.level_name,
            property_name=key,
        )

        identifier = get_property_output.data_model.cube.dimension.hierarchy.level.member_property
        if identifier is None:
            return {}
        return {identifier.name: ColumnIdentifier._from_graphql(identifier.column)}

    @override
    def _update_delegate(
        self,
        other: Mapping[str, Identifiable[ColumnIdentifier]],
        /,
    ) -> None:
        graphql_client = self._client._require_graphql_client()

        fields: list[GraphQLField] = []
        for name, column in other.items():
            column_identifier = identify(column)
            mutation_input = CreateMemberPropertyInput(
                column_name=column_identifier.column_name,
                cube_name=self._cube_identifier.cube_name,
                level_identifier=self._level_identifier._graphql_input,
                property_name=name,
                table_name=column_identifier.table_identifier.table_name,
            )
            fields.append(Mutation.create_member_property(mutation_input))
        graphql_client.mutation(*fields, operation_name="UpdateMemberProperties")

    @override
    def _delete_delegate_keys(self, _keys: AbstractSet[str], /) -> None:
        keys = list(_keys)
        del _keys

        fields: list[GraphQLField] = []

        for key in keys:
            mutation_input = DeleteMemberPropertyInput(
                cube_name=self._cube_identifier.cube_name,
                level_identifier=self._level_identifier._graphql_input,
                property_name=key,
            )
            field = Mutation.delete_member_property(mutation_input)
            field.fields(field.status)
            fields.append(field)

        raw_output = self._client._require_graphql_client().mutation(
            *fields, operation_name="DeleteMemberProperties"
        )
        output = get_type_adapter(_DeleteMemberPropertiesOutput).validate_python(  # type: ignore[type-abstract]
            raw_output
        )
        del raw_output

        for index, delete_member_property_output in enumerate(output.values()):
            match delete_member_property_output.status.value:
                case "DELETED":
                    ...
                case "NOT_FOUND":
                    member_property_name: str = keys[index]
                    raise KeyError(member_property_name)
