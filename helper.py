from datetime import datetime, time

day_dict = {
    "Sunday": 0,
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6
}

# period_dict = {
#     "Overnight": 1,
#     "Early Morning": 2,
#     "AM Peak": 3,
#     "Midday": 4,
#     "Early Afternoon": 5,
#     "PM Peak": 6,
#     "Evening": 7
# }

period_dict = {
    "Overnight": {"id": 1, 
                  "start_time": "00:00", 
                  "end_time": "03:59"},
    "Early Morning": {"id": 2, 
                      "start_time": "04:00", 
                      "end_time": "06:59"},
    "AM Peak": {"id": 3, 
                "start_time": "07:00", 
                "end_time": "09:59"},
    "Midday": {"id": 4, 
               "start_time": "10:00", 
               "end_time": "12:59"},
    "Early Afternoon": {"id": 5, 
                        "start_time": "13:00", 
                        "end_time": "15:59"},
    "PM Peak": {"id": 6, 
                "start_time": "16:00", 
                "end_time": "18:59"},
    "Evening": {"id": 7, 
                "start_time": "19:00", 
                "end_time": "23:59"}
}

def convert_period_string_to_datetimes(period=None):
    if period:
        period_details = period_dict.get(period, None)
        if period_details is None:
            return None, None
        start_time = datetime.strptime(period_details.get("start_time", "00:00"), "%H:%M").time()
        end_time = datetime.strptime(period_details.get("end_time", "00:00"), "%H:%M").time()

        # hardcoded due to data dump only being for 2024-01-01
        # the assignement does not specify an actual date
        # normally you would obviously not hard code this
        db_date_string = "2024-01-01T18:00:00.000Z"
        db_date = datetime.fromisoformat(db_date_string.replace("Z", "+00:00"))

        start_datetime = datetime.combine(db_date.date(), start_time)
        end_datetime = datetime.combine(db_date.date(), end_time)
        
        start_datetime_str = start_datetime.isoformat()
        end_datetime_str = end_datetime.isoformat()

        return start_datetime_str, end_datetime_str
    return None, None