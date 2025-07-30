import datetime

def timestamp_to_datetime(timestamp):
    """
    Converts a timestamp string to a datetime object.
    Args:
       timestamp (str): The timestamp string in the format "%Y-%m-%dT%H:%M:%S.%f"
    """
    try:
        result = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        result = date_string
    return result
   