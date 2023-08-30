import pandas as pd
from bs4 import BeautifulSoup
import requests
import pytz
from datetime import datetime


class sofaScore:

    def current_timezone(self):
        current_datetime = datetime.now()

        # Convert the datetime to GMT/UTC timezone
        gmt_timezone = pytz.timezone('GMT')
        current_datetime_utc = gmt_timezone.localize(current_datetime)

        # Format the datetime
        formatted_datetime = current_datetime_utc.strftime(
            '%a, %d %b %Y %H:%M:%S %Z')

        return formatted_datetime

    # def get_
