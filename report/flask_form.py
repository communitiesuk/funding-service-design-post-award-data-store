from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput
from wtforms import Field, SubmitField
from wtforms.fields.core import UnboundField


class CustomFlaskForm(FlaskForm):
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_as_draft = SubmitField("Save as draft", widget=GovSubmitInput())

    def get_input_data(self):
        return {
            field_name: field.data
            for field_name, field in self.__dict__.items()
            if isinstance(field, (Field, UnboundField))
            and not isinstance(field, SubmitField)
            and field_name != "csrf_token"
        }
