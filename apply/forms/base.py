from flask_wtf import FlaskForm
from wtforms import HiddenField


# Always has an application_id, as it's required by @verify_application_owner_local on POST requests.
class ApplicationFlaskForm(FlaskForm):
    application_id = HiddenField()


class PrepopulatedForm(ApplicationFlaskForm):
    def back_fill_data(self, data: dict):
        for field_name, field in self._fields.items():
            if field_name != "application_id":
                field.data = data.get(field_name)

    def as_dict(self):
        return {field_name: field.data for field_name, field in self._fields.items() if field_name != "application_id"}
