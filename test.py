import datetime
def get_target_date():
    # Today's date
    current_date = datetime.datetime.now()

    # Target date (2 week ahead)
    delta_date = datetime.timedelta(14)
    target_date = current_date + delta_date
    month_string = "%#m"
    day_string = "%#d"
    target_month = target_date.strftime(month_string)
    target_day = target_date.strftime(day_string)
    return target_month, target_day

target_month, target_day = get_target_date()
print(str(int(target_month)-1), target_day)