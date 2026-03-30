"""
WTForms definitions
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import FloatField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class EmployeeForm(FlaskForm):
    """Shared employee fields"""

    img_employee = FileField("Photo")
    ic = StringField("IC / Passport", validators=[DataRequired()])
    contact = StringField("Contact")
    address = StringField("Address")
    pay_hour = FloatField("Hourly Rate (RM)", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CreateEmployeeForm(EmployeeForm):
    """Form for creating new employee"""

    name = StringField("Name", validators=[DataRequired()])
    dob = StringField("Date of Birth")
    gender = SelectField(
        "Gender", choices=["", "male", "female"]
    )
    nationality = SelectField(
        "Nationality",
        choices=[
            "",
            "Malaysia",
            "Indonesia",
            "Bangladesh",
            "Rohingya",
            "Other",
        ],
    )


class EditEmployeeForm(EmployeeForm):
    """Form for editing existing employee"""

    pass


CreateForm = CreateEmployeeForm
EditForm = EditEmployeeForm
