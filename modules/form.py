"""
Form module
CreateForm, EditForm
"""
from flask_wtf import FlaskForm
from wtforms import (EmailField, FileField, FloatField, PasswordField,
                     SelectField, StringField, SubmitField, validators)


# Class Create Form
class CreateForm(FlaskForm):
    """Create Form and inherent to Edit Form"""

    # validators
    img_employee = FileField("img_employee")
    name = StringField("name", [validators.DataRequired()])
    ic = StringField("passport / ic", [validators.DataRequired()])
    pay_hour = FloatField("hour salary", [validators.DataRequired()])

    # Optional
    dob = StringField("d.o.b")
    gender = SelectField("gender", choices=["Please select", "male", "female"])
    nationality = SelectField(
        "nationality",
        choices=[
            "Please select",
            "Malaysia",
            "Indonesia",
            "Bangladesh",
            "Rohingya",
            "Other",
        ],
    )
    contact = StringField("contact")
    address = StringField("address")

    submit = SubmitField("submit")


# Class Edit Form
class EditForm(FlaskForm):
    """Edit Form"""

    img_employee = FileField("img_employee")
    ic = StringField("passport / ic")
    contact = StringField("contact")
    address = StringField("address")
    pay_hour = FloatField("pay hour")

    submit = SubmitField("submit")



class LoginForm(FlaskForm):
    """Login Form"""

    username = EmailField("email", [validators.DataRequired()])
    password = PasswordField("password", [validators.DataRequired()])

    submit = SubmitField("submit")


class RegisterForm(FlaskForm):
    """Register Form"""

    username = EmailField("email", [validators.DataRequired(), validators.Email()])
    password = PasswordField("password", [validators.DataRequired(message="Please fill password")])
    company_name = StringField("company name", [validators.DataRequired(message="Please fill full company name")])

    submit = SubmitField("submit")
