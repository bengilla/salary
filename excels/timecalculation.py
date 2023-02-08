import pendulum

class TimeCalculation:
    """TimeCalculation 是计算所有员工的上下班时间"""

    def __init__(self, emp_time, emp_salary):
        self.emp_time: list = emp_time
        self.emp_salary: float = emp_salary
        self.emp_work_hour: int = 0

    def result(self, num):
        """功能：计算时间，把时间换成工资计算"""
        if self.emp_time[num] == 0 or len(self.emp_time[num]) < 2:
            return 0

        elif isinstance(self.emp_time[num], list):
            emp_in = pendulum.parse(self.emp_time[num][0])
            emp_out = pendulum.parse(self.emp_time[num][-1])
            day_in = pendulum.parse("08:35")
            day_out = pendulum.parse("17:25")

            # 午餐
            lunch_time = 1  # Lunch Time
            # 祈祷
            sembahyang = 2

            # 计算白天的工作时间 -----------------------------------------
            # 正常
            if emp_in <= day_in and emp_out >= day_out:
                self.emp_work_hour += 8
            # 早到 早退
            elif emp_in <= day_in and emp_out <= day_out:
                total_times = pendulum.period(day_in, emp_out)
                if total_times.hours > 4:
                    self.emp_work_hour += total_times.hours - lunch_time
                    if total_times.minutes >= 50:
                        self.emp_work_hour += 1
                else:
                    self.emp_work_hour += total_times.hours
                    if total_times.minutes >= 50:
                        self.emp_work_hour += 1
            # 晚到 晚退
            elif emp_in >= day_in and emp_out >= day_out:
                total_times = pendulum.period(emp_in, day_out)
                if total_times.hours > 4:
                    self.emp_work_hour += total_times.hours - lunch_time
                    if total_times.minutes >= 50:
                        self.emp_work_hour += 1
                else:
                    self.emp_work_hour += total_times.hours
                    if total_times.minutes >= 50:
                        self.emp_work_hour += 1

            # 计算加班 -------------------------------------------------
            overtime = [
                "18:10",
                "18:55",
                "19:40",
                "20:25",
                "21:10",
                "21:55",
                "22:55",
                "23:55",
            ]
            for time in overtime:
                if emp_out >= pendulum.parse(time):
                    self.emp_work_hour += 1

            return self.emp_work_hour * self.emp_salary
