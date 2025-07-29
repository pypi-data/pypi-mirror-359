# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AddColumnBase"]


class AddColumnBase(BaseModel):
    cardinality: Literal["one", "many"]

    lookup_external_column_id: str = FieldInfo(alias="lookupExternalColumnId")

    lookup_source_column_id: str = FieldInfo(alias="lookupSourceColumnId")

    name: str

    type: Literal["lookup"]

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)
