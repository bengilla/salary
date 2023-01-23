"""
Form module
CreateForm, EditForm
"""
from fastapi import Form
from pydantic import BaseModel, Field
# from wtforms import (EmailField, FileField, FloatField, PasswordField,
                    #  SelectField, StringField, SubmitField, validators)


# Class Create Form
# class CreateForm():
#     """Create Form and inherent to Edit Form"""

#     # validators
#     img_employee = FileField("img_employee")
#     name = StringField("name", [validators.DataRequired()])
#     ic = StringField("passport / ic", [validators.DataRequired()])
#     pay_hour = FloatField("hour salary", [validators.DataRequired()])

#     # Optional
#     dob = StringField("d.o.b")
#     gender = SelectField("gender", choices=["Please select", "male", "female"])
#     nationality = SelectField(
#         "nationality",
#         choices=[
#             "Please select",
#             "Malaysia",
#             "Indonesia",
#             "Bangladesh",
#             "Rohingya",
#             "Other",
#         ],
#     )
#     contact = StringField("contact")
#     address = StringField("address")

#     submit = SubmitField("submit")


# Class Edit Form
# class EditForm():
#     """Edit Form"""

#     img_employee = FileField("img_employee")
#     ic = StringField("passport / ic")
#     contact = StringField("contact")
#     address = StringField("address")
#     pay_hour = FloatField("pay hour")

#     submit = SubmitField("submit")



class LoginForm(BaseModel):
    """Login Form"""
    email: str = Field(...)
    password: str = Field(...)

    @classmethod
    def login(
        cls,
        email: str = Form(...),
        password: str = Form(...)
    ):
        return cls(
            email=email,
            password=password
        )


class RegisterForm(BaseModel):
    """Register Form"""
    email: str
    password: str
    company_name: str

    @classmethod
    def register(
        cls,
        email: str = Form(...),
        password: str = Form(...),
        company_name: str = Form(...)
    ):
        return cls(
            email=email,
            password=password,
            company_name=company_name
        )
