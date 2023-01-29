"""
Form module
CreateForm, EditForm
"""
from fastapi import Form
from pydantic import BaseModel, Field
# from wtforms import (EmailField, FileField, FloatField, PasswordField,
                    #  SelectField, StringField, SubmitField, validators)


# Class Create Form
class CreateForm(BaseModel):
    """Create Form and inherent to Edit Form"""

    # validators
    # img_employee = FileField("img_employee")
    name: str = Field(...)
    ic: str = Field(...)
    pay_hour: float = Field(...)

    # Optional
    dob: str = Field(...)
    gender: str = Field(...)
    nationality: str = Field(...)
    # gender = SelectField("gender", choices=["Please select", "male", "female"])
    # nationality = SelectField(
    #     "nationality",
    #     choices=[
    #         "Please select",
    #         "Malaysia",
    #         "Indonesia",
    #         "Bangladesh",
    #         "Rohingya",
    #         "Other",
    #     ],
    # )
    contact: int | None = Field(...)
    address: str = Field(...)

    @classmethod
    def create_form(
        cls,
        name: str = Form(...),
        ic: str = Form(...),
        pay_hour: float = Form(...),
        dob: str = Form(...),
        gender: str = Form(...),
        nationality: str = Form(...),
        contact: int = Form(...),
        address: str = Form(...)
    ):
        return cls(
            nme=name,
            ic=ic,
            pay_hour=pay_hour,
            dob=dob,
            gender=gender,
            nationality=nationality,
            contact=contact,
            address=address
        )


# Class Edit Form
class EditForm(BaseModel):
    """Edit Form"""
    # img_employee = FileField("img_employee")
    ic: str = Field(...)
    contact: int = Field(...)
    address: str = Field(...)
    pay_hour: float = Field(...)

    @classmethod
    def edit_form(
        cls,
        ic: str = Form(...),
        contact: int = Form(...),
        address: str = Form(...),
        pay_hour: float = Form(...)
    ):
        return cls(
            ic=ic,
            contact=contact,
            address=address,
            pay_hour=pay_hour
        )




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
