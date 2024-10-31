from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import DataRequired
from wtforms.validators import NumberRange


def not_eligible_page(message):
    flash(message)
    return redirect(url_for("routes.not_eligible"))


def minimium_money_question_page(max_amount: int, success_url: str, data_hook: callable = print):
    """
    Returns a Flask view function which checks the eligibility
    of a fund using the gov.uk design system.

    Args:
        max_amount (int): The maximium amount one can apply for.
        success_url (str): The url one is redirected to if eliglible.
        data_hook (callable): This function will be ran on the inputted
        data if the fund is eligible. By default prints to console.

    Returns:
        function: A function which renders a template.
    """

    class MinimiumMoneyForm(FlaskForm):

        money_field = IntegerField(
            label="project_money_amount",
            validators=[DataRequired(), NumberRange(max=max_amount)],
        )

    def min_money_page():

        form = MinimiumMoneyForm()
        # If the user has entered data and they are not valid...
        if request.method == "POST":
            if form.validate_on_submit():
                data_hook(form.money_field.data)
                return render_template(
                    "eligible.html",
                    service_url=success_url,
                )
            else:
                # ...then flash the message and redirect.
                return not_eligible_page(f"You can apply for a maximium amount of £{max_amount}.")

        return render_template("min_funding_amount.html", form=form)

    return min_money_page()
