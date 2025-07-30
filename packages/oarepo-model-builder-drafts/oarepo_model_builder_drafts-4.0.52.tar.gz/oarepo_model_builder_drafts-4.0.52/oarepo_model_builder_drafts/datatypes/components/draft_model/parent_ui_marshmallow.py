import marshmallow as ma
from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import (
    DefaultsModelComponent,
    MarshmallowModelComponent,
)
from oarepo_model_builder.datatypes.components.model.utils import set_default
from oarepo_model_builder.validation.utils import ImportSchema

from oarepo_model_builder_drafts.datatypes.components.draft_model.parent_marshmallow import ParentMarshmallowClassSchema


class ParentUIMarshmallowComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [DefaultsModelComponent, MarshmallowModelComponent]

    class ModelSchema(ma.Schema):
        parent_record_ui_marshmallow = ma.fields.Nested(
            ParentMarshmallowClassSchema,
            attribute="parent-record-ui-marshmallow",
            data_key="parent-record-ui-marshmallow",
        )

    def before_model_prepare(self, datatype, *, context, **kwargs):
        marshmallow = set_default(datatype, "parent-record-ui-marshmallow", {})
        m_module = marshmallow.setdefault(
            "module", datatype.definition["ui"]["marshmallow"]["module"]
        )
        marshmallow.setdefault("class", f"{m_module}.GeneratedParentUISchema")
        marshmallow.setdefault("generate", False)
        marshmallow.setdefault(
            "base-classes",
            [
                "invenio_drafts_resources.services.records.schema.ParentSchema"
            ],
        )
