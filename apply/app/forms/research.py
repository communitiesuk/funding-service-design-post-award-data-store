from app.forms.base import PrepopulatedForm
from flask_babel import gettext
from flask_babel import lazy_gettext
from wtforms import RadioField
from wtforms import StringField
from wtforms.validators import Email
from wtforms.validators import InputRequired


class ResearchOptForm(PrepopulatedForm):
    research_opt_in = RadioField(
        validators=[InputRequired(message="Select an option")],
    )

    def __init__(self, *args, **kwargs):
        super(ResearchOptForm, self).__init__(*args, **kwargs)
        self.research_opt_in.choices = [
            ("agree", gettext("I agree to be contacted for research purposes")),
            ("disagree", gettext("I do not want to be contacted for research purposes")),
        ]


class ResearchContactDetailsForm(PrepopulatedForm):
    contact_email_input_message = lazy_gettext("Contact email address is required")
    contact_name_input_message = lazy_gettext("Name of contact is required")
    contact_name = StringField(label="Full name", validators=[InputRequired(message=contact_name_input_message)])
    contact_email = StringField(label="Email", validators=[InputRequired(message=contact_email_input_message), Email()])
