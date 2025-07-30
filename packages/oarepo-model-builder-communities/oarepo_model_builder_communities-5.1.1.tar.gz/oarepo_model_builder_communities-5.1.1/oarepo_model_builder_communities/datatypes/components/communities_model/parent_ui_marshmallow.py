from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components.model.utils import set_default
from oarepo_model_builder_drafts.datatypes.components import ParentUIMarshmallowComponent



class CommunitiesParentUIMarshmallowComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    affects = [ParentUIMarshmallowComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        marshmallow = set_default(datatype, "parent-record-ui-marshmallow", {})
        marshmallow.setdefault("generate", True)
