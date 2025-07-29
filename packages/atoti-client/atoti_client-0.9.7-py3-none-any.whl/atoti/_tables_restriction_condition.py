from __future__ import annotations

from typing import Literal, TypeAlias

from ._constant import Str
from ._identification import ColumnIdentifier
from ._operation import LogicalCondition, MembershipCondition, RelationalCondition

_TablesRestrictionLeafCondition: TypeAlias = (
    MembershipCondition[ColumnIdentifier, Literal["in"], Str]
    | RelationalCondition[ColumnIdentifier, Literal["=="], Str]
)
TablesRestrictionCondition: TypeAlias = (
    _TablesRestrictionLeafCondition
    | LogicalCondition[_TablesRestrictionLeafCondition, Literal["&"]]
)
