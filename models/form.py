from fastapi import Form, File, UploadFile
from pydantic import BaseModel

# Login and Register Form Sections ------------------------------
class LoginForm(BaseModel):
    email: str
    password: str

    @classmethod
    def login(cls, email: str = Form(...), password: str = Form(...)):
        return cls(email=email, password=password)

class RegisterForm(LoginForm):
    company_name: str

    @classmethod
    def register(cls, email: str = Form(...), password: str = Form(...), company_name: str = Form(...)):
        return cls(email=email, password=password, company_name=company_name)

# Users create, edit and delete forms ------------------------------
class EmpForm(BaseModel):
    img_emp: UploadFile
    pay_hour: float = None
    ic: str = None
    contact: str = None
    address: str = None

class CreateForm(EmpForm):
    name: str
    dob: str = None
    gender: str = None
    nationality: str = None

    @classmethod
    def create(
        cls,
        name: str = Form(...),
        pay_hour: float = Form(...),
        # Optional
        img_emp: UploadFile = File(None),
        ic: str = Form(None),
        dob: str = Form(None),
        gender: str = Form(None),
        nationality: str = Form(None),
        contact: str = Form(None),
        address: str = Form(None)
    ):
        return cls(
            img_emp=img_emp,
            name=name.title(),
            ic=ic,
            pay_hour=pay_hour,
            dob=dob,
            gender=gender,
            nationality=nationality,
            contact=contact,
            address=address
        )

class EditForm(EmpForm):
    
    @classmethod
    def edit(
        cls,
        img_emp: UploadFile = File(None),
        ic: str = Form(None),
        pay_hour: float = Form(None),
        contact: str = Form(None),
        address: str = Form(None),
    ):
        return cls(
            img_emp=img_emp,
            ic=ic,
            pay_hour=pay_hour,
            contact=contact,
            address=address,
        )

# form for upload excel file ------------------------------
class ExcelForm(BaseModel):
    excel: UploadFile

    @classmethod
    def excel_upload(
            cls,
            excel: UploadFile = File(None),
    ):
        return cls(
            excel=excel,
        )
