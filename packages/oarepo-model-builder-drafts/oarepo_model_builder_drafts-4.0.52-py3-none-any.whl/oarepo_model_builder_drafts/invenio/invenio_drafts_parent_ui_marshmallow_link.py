from oarepo_model_builder_drafts.invenio.invenio_drafts_parent_ui_marshmallow import \
    InvenioDraftsParentUIMarshmallowBuilder


class InvenioDraftsParentUIMarshmallowLinkBuilder(InvenioDraftsParentUIMarshmallowBuilder):
    TYPE = "invenio_drafts_parent_ui_marshmallow_link"
    section = "parent-record-ui-marshmallow"
    template = "drafts-parent-ui-marshmallow-link"
