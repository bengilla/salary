"""
Emp operation function
"""

import datetime as dt

# 自身库
from forms.form import CreateForm
from modules.image import ImageConvert
from mongodb import MongoDB

# 建立员工模组


class EmpInfo:
    """工作与员工讯息"""

    def __init__(self) -> None:
        """
        加载 mongodb 链接与读取
        """
        mongodb = MongoDB()
        self.emp_info_collection = mongodb.info_collection()
        self.img_convert = ImageConvert()

    def emp_create(self) -> bool:
        """
        建立员工资料\n
        """
        form = CreateForm()
        date = dt.datetime.now().strftime("%d-%m-%Y")

        def check_emp():
            """
            检查是否员工已经入库
            """
            store_emp_ic = []
            get_emp = self.emp_info_collection.find({})
            for emp_ic in get_emp:
                store_emp_ic.append(emp_ic["ic"])
            return store_emp_ic

        # 如果员工不在库里，执行
        if form.ic.data not in check_emp():
            new_emp = {
                # "_id": form.name.data.split(" ")[0].lower() + form.ic.data[-4:],
                "_id": form.name.data.split(" ")[0].lower(),
                "img_employee": self.img_convert.img_base64(form.img_employee.data),
                "name": form.name.data.title(),
                "ic": form.ic.data,
                "pay_hour": form.pay_hour.data,
                "dob": form.dob.data,
                "nationality": form.nationality.data,
                "gender": form.gender.data,
                "contact": form.contact.data,
                "address": form.address.data,
                "sign_date": date,
                # "finger_print": int(form.finger_print.data),
            }
            self.emp_info_collection.insert_one(new_emp)
            return True
        else:
            return False

    def emp_info(self):
        """
        读取所有员工资料
        """
        results = self.emp_info_collection.find({})
        return results

    def emp_one(self, ids: str):
        """
        读取单位员工资料
        """
        result = self.emp_info_collection.find_one({"_id": ids})
        return result

    def emp_delete(self, ids: str):
        """
        删除员工资料
        """
        self.emp_info_collection.delete_one({"_id": ids})

    def emp_edit(self, ids, ic_card, contact, address, pay, img_employee):
        """
        更新员工资料
        """
        get_id = {"_id": ids}

        if img_employee:
            self.emp_info_collection.update_one(
                get_id,
                {
                    "$set": {
                        "img_employee": self.img_convert.img_base64(img_employee),
                        "ic": ic_card,
                        "contact": contact,
                        "address": address,
                        "pay_hour": pay,
                    }
                },
            )
        else:
            self.emp_info_collection.update_one(
                get_id,
                {
                    "$set": {
                        "ic": ic_card,
                        "contact": contact,
                        "address": address,
                        "pay_hour": pay,
                    }
                },
            )
