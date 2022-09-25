"""
Emp operation function
"""

import datetime as dt
from base64 import b64encode
from io import BytesIO

from PIL import Image

# 自身库
from forms import CreateForm
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

    def emp_create(self) -> bool:
        """
        建立员工资料\n
        """
        form = CreateForm()
        date = dt.datetime.now().strftime("%d-%m-%Y")

        def img_convert(img_input: str):
            """
            img 压缩成 Binary 代码\n
            """
            # try:
            base_width = 300
            buffered = BytesIO()
            img = Image.open(img_input)
            width_percent = base_width / float(img.size[0])
            height_size = int((float(img.size[1]) * float(width_percent)))
            img_resize = img.resize((base_width, height_size), Image.ANTIALIAS)
            img_resize.save(buffered, format="JPEG")
            return b64encode(buffered.getvalue()).decode("ascii")
            # except:
            #     raise Exception("Please upload image")

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
                "img_emp": img_convert(form.img_emp.data),
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

    def emp_edit(self, ids, ic_card, contact, address, pay):
        """
        更新员工资料
        """
        get_id = {"_id": ids}
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
