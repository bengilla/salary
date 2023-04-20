"""Form Section"""
from fastapi import Form, File, UploadFile
from pydantic import BaseModel


# Login and Register Form Sections ------------------------------
class LoginForm(BaseModel):
    """Login Forms"""

    email: str
    password: str

    @classmethod
    def login(cls, email: str = Form(...), password: str = Form(...)):
        """login"""
        return cls(email=email, password=password)


class RegisterForm(LoginForm):
    """Register Form"""

    company_name: str

    @classmethod
    def register(
        cls,
        email: str = Form(...),
        password: str = Form(...),
        company_name: str = Form(...),
    ):
        """register"""
        return cls(email=email, password=password, company_name=company_name)


class RegisterFormWithCode(RegisterForm):
    """Register Form"""

    code: str

    @classmethod
    def register(
        cls,
        email: str = Form(...),
        password: str = Form(...),
        company_name: str = Form(...),
        code: str = Form(...),
    ):
        """register"""
        return cls(email=email, password=password, company_name=company_name, code=code)


# Users create, edit and delete forms ------------------------------
class EmpForm(BaseModel):
    """General Emp Form"""

    img_emp: UploadFile
    pay_hour: float = None
    ic: str = None
    contact: str = None
    address: str = None


class CreateForm(EmpForm):
    """Create Form"""

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
        id_card: str = Form(None),
        dob: str = Form(None),
        gender: str = Form(None),
        nationality: str = Form(None),
        contact: str = Form(None),
        address: str = Form(None),
    ):
        """create"""
        return cls(
            img_emp=img_emp,
            name=name.title(),
            ic=id_card,
            pay_hour=pay_hour,
            dob=dob,
            gender=gender,
            nationality=nationality,
            contact=contact,
            address=address,
        )


class EditForm(EmpForm):
    """Edit Form"""

    @classmethod
    def edit(
        cls,
        img_emp: UploadFile = File(None),
        id_card: str = Form(None),
        pay_hour: float = Form(None),
        contact: str = Form(None),
        address: str = Form(None),
    ):
        """edit"""
        return cls(
            img_emp=img_emp,
            ic=id_card,
            pay_hour=pay_hour,
            contact=contact,
            address=address,
        )


# form for upload excel file ------------------------------
class ExcelForm(BaseModel):
    """Excel Form"""

    excel: UploadFile

    @classmethod
    def excel_upload(
        cls,
        excel: UploadFile = File(None),
    ):
        """excel upload"""
        return cls(
            excel=excel,
        )
