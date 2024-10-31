from app.forms.base import ApplicationFlaskForm
from app.forms.base import PrepopulatedForm
from flask_babel import gettext
from wtforms import FloatField
from wtforms import RadioField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired
from wtforms.validators import NumberRange


class DefaultSectionFeedbackForm(ApplicationFlaskForm):
    experience = RadioField()
    more_detail = TextAreaField()

    def __init__(self, *args, **kwargs):
        super(DefaultSectionFeedbackForm, self).__init__(*args, **kwargs)
        self.experience.label.text = gettext("How easy did you find it to complete this section?")
        self.experience.choices = [
            ("very easy", gettext("Very easy")),
            ("easy", gettext("Easy")),
            (
                "neither easy or difficult",
                gettext("Neither easy nor difficult"),
            ),
            ("difficult", gettext("Difficult")),
            ("very difficult", gettext("Very difficult")),
        ]
        self.more_detail.label.text = gettext("Explain why you chose this score (optional)")
        self.experience.validators = [InputRequired(message=gettext("Select a score"))]

    @property
    def as_dict(self):
        return {
            "application_id": self.application_id.data,
            "experience": self.experience.data,
            "more_detail": self.more_detail.data,
        }


class EndOfApplicationPage1Form(PrepopulatedForm):
    overall_application_experience = RadioField()
    more_detail = TextAreaField()

    def __init__(self, *args, **kwargs):
        super(EndOfApplicationPage1Form, self).__init__(*args, **kwargs)
        self.overall_application_experience.label.text = gettext("How was your overall application experience?")
        self.overall_application_experience.choices = [
            ("very good", gettext("Very good")),
            ("good", gettext("Good")),
            ("average", gettext("Average")),
            ("poor", gettext("Poor")),
            ("very poor", gettext("Very poor")),
        ]
        self.more_detail.label.text = gettext("Explain why you chose this score (optional)")
        self.overall_application_experience.validators = [InputRequired(message=gettext("Select a score"))]


class EndOfApplicationPage2Form(PrepopulatedForm):
    demonstrate_why_org_funding = RadioField()

    def __init__(self, *args, **kwargs):
        super(EndOfApplicationPage2Form, self).__init__(*args, **kwargs)
        self.demonstrate_why_org_funding.label.text = gettext(
            "To what extent do you agree that this application form allowed"
            " you to demonstrate why your organization should receive funding?"
        )
        self.demonstrate_why_org_funding.choices = [
            ("strongly agree", gettext("Strongly agree")),
            ("agree", gettext("Agree")),
            (
                "neither agree nor disagree",
                gettext("Neither agree nor disagree"),
            ),
            ("disagree", gettext("Disagree")),
            ("strongly disagree", gettext("Strongly disagree")),
        ]
        self.demonstrate_why_org_funding.validators = [InputRequired(message=gettext("Select a score"))]


class EndOfApplicationPage3Form(PrepopulatedForm):
    understand_eligibility_criteria = RadioField()

    def __init__(self, *args, **kwargs):
        super(EndOfApplicationPage3Form, self).__init__(*args, **kwargs)
        self.understand_eligibility_criteria.label.text = gettext(
            "How easy was it to understand the eligibility criteria for this fund?"
        )
        self.understand_eligibility_criteria.choices = [
            ("very easy", gettext("Very easy")),
            ("easy", gettext("Easy")),
            (
                "neither easy or difficult",
                gettext("Neither easy nor difficult"),
            ),
            ("difficult", gettext("Difficult")),
            ("very difficult", gettext("Very difficult")),
        ]
        self.understand_eligibility_criteria.validators = [InputRequired(message=gettext("Select a score"))]


class EndOfApplicationPage4Form(PrepopulatedForm):
    hours_spent = FloatField()

    def __init__(self, *args, **kwargs):
        super(EndOfApplicationPage4Form, self).__init__(*args, **kwargs)
        self.hours_spent.label.text = gettext("Number of hours spent:")
        self.hours_spent.validators = [
            DataRequired(message=gettext("Enter a number only. The number must be at least 0.5 or greater.")),
            NumberRange(min=0.5),
        ]


END_OF_APPLICATION_FEEDBACK_SURVEY_PAGE_NUMBER_MAP = {
    "1": (
        EndOfApplicationPage1Form,
        "end_of_application_feedback_page_1.html",
    ),
    "2": (
        EndOfApplicationPage2Form,
        "end_of_application_feedback_page_2.html",
    ),
    "3": (
        EndOfApplicationPage3Form,
        "end_of_application_feedback_page_3.html",
    ),
    "4": (
        EndOfApplicationPage4Form,
        "end_of_application_feedback_page_4.html",
    ),
}
