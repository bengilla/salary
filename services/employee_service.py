"""
Employee management service
"""

import datetime as dt
from typing import Optional

from models import Employee
from mongodb import get_mongodb
from utils.image import ImageConverter


class EmployeeService:
    """Employee CRUD operations"""

    def __init__(self):
        self._db = get_mongodb()
        self._img_converter = ImageConverter()

    def _generate_id(self, name: str, ic: str) -> str:
        """Generate unique employee ID from name and IC"""
        base_id = name.split(" ")[0].lower()
        existing_ids = [emp["_id"] for emp in self.list_all()]
        if base_id not in existing_ids:
            return base_id
        suffix = ic[-4:] if len(ic) >= 4 else ic
        new_id = f"{base_id}{suffix}"
        counter = 1
        while new_id in existing_ids:
            new_id = f"{base_id}{suffix}{counter}"
            counter += 1
        return new_id

    def create(
        self,
        name: str,
        ic: str,
        pay_hour: float,
        img_employee,
        dob: str = "",
        nationality: str = "",
        gender: str = "",
        contact: str = "",
        address: str = "",
    ) -> bool:
        """Create new employee"""
        existing_ics = [emp["ic"] for emp in self.list_all()]
        if ic in existing_ics:
            return False

        emp_id = self._generate_id(name, ic)
        img_base64 = self._img_converter.to_base64(img_employee) if img_employee else ""

        doc = {
            "_id": emp_id,
            "name": name.title(),
            "ic": ic,
            "pay_hour": pay_hour,
            "img_employee": img_base64,
            "dob": dob,
            "nationality": nationality,
            "gender": gender,
            "contact": contact,
            "address": address,
            "sign_date": dt.datetime.now().strftime("%d-%m-%Y"),
        }
        self._db.info_collection.insert_one(doc)
        return True

    def list_all(self) -> list:
        """Get all employees"""
        return list(self._db.info_collection.find({}))

    def get_one(self, emp_id: str) -> Optional[dict]:
        """Get single employee by ID"""
        return self._db.info_collection.find_one({"_id": emp_id})

    def update(
        self,
        emp_id: str,
        ic_card: str,
        contact: str,
        address: str,
        pay: float,
        img_employee=None,
    ) -> None:
        """Update employee information"""
        update_data = {
            "ic": ic_card,
            "contact": contact,
            "address": address,
            "pay_hour": pay,
        }
        if img_employee:
            update_data["img_employee"] = self._img_converter.to_base64(img_employee)

        self._db.info_collection.update_one(
            {"_id": emp_id}, {"$set": update_data}
        )

    def delete(self, emp_id: str) -> None:
        """Delete employee"""
        self._db.info_collection.delete_one({"_id": emp_id})
