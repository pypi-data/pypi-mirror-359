from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioDraftsParentUIMarshmallowBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_drafts_parent_ui_marshmallow"
    section = "parent-record-ui-marshmallow"
    template = "drafts-parent-ui-marshmallow"

    """
    def finish(self, **extra_kwargs):
        super().finish()
        if not self.generate:
            return

        module = self._get_output_module()
        python_path = Path(module_to_path(module) + ".py")

        self.process_template(
            python_path,
            self.template,
            current_module=module,
            vars=self.vars,
            **extra_kwargs,
        )
    """
