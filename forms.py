"""
Form module
CreateForm, EditForm
"""


from flask_wtf import FlaskForm
from wtforms import FileField, FloatField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


# Class Edit Form
class EditForm(FlaskForm):
    """Edit Form"""

    ic = StringField("passport / ic")
    contact = StringField("contact")
    address = StringField("address")
    pay_hour = FloatField("pay hour")

    submit = SubmitField("submit")


# Class Create Form
# Inherent Edit Form
class CreateForm(EditForm, FlaskForm):
    """Create Form and inherent to Edit Form"""

    img_emp = FileField("img_emp", validators=[DataRequired()])
    name = StringField("name", validators=[DataRequired()])
    pay_hour = FloatField("hour salary", validators=[DataRequired()])
    ic = StringField("passport / ic", validators=[DataRequired()])

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
    finger_print = StringField("finger print")
