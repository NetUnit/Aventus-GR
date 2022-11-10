import requests
from datetime import datetime
import datetime as dt

import requests
import json
import base64

# setting env variables
from decouple import config
from django.core.exceptions import ValidationError

class ProcessReport():
    '''
    (1) iso_date = "2022-12-31 23:59:58" string
    datetime.strptime(iso_date, "%Y-%m-%d") - converts str to datetime obj
    with pattern "yyyy-mm-dd" 
    (2) datetime_obj = datetime(2022, 12, 31) dt object
    datetime.strftime(datetime_obj, "%Y-%m-%d") - converts a datetime object
    to a string with preset pattern
    '''

    auth_header = {'Authorization': None}
    params = {"LoadDate": None, "Days": None}

    # time converter --> to date yyyy-mm-dd
    to_date = lambda datetime: datetime.strftime("%Y-%m-%d")
    
    # ISO format
    iso_format = "%Y-%m-%d"

    # adjust to get another report (put your report url here)
    # url = config('LK_DIRECT_COMMUNICATIONS')
    url = config('KE_CLIENTS_W')

    # adjust dates
    start_date = "2021-09-29"
    end_date = "2021-10-30"

    # adjust to get valid token (put your token report url here)
    token_url = config('KE_TOKEN_URL')
    login = config('LOGIN_KE')
    password = config('PASSWORD')

    latency = None
    latency_data = dict()

    days = 1

    def get_month_from_num(self, month_num):
        datetime_object = datetime.strptime(str(month_num), "%m")

        month_name = datetime_object.strftime("%b")
        full_month_name = datetime_object.strftime("%B")
        self.month = full_month_name
        return full_month_name

    def save_latency_data(self, month, latency):
        self.latency_data[month] = latency
        return self


    def get_token(self, token_url=None, login=None, password=None):

        # login is value set to method or got from local environment
        login = self.login if login is None else login
        password = self.password if password is None else password

        # "dwh_service_pl:AvGr220717"
        userAndPassword = base64.b64encode(
            str(login + ":" + password).encode(encoding='UTF-8')
        ).decode("ascii")

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': "Basic " + userAndPassword
        }

        payload = 'username=rostyslav.mazepa%40gmail.com'\
            '&password=MaRo210583&grant_type=password'

        response = requests.request("POST", self.token_url, data=payload,
                                    headers=headers)

        json_token = json.loads(response.text)
        access_token = json_token.get("access_token")
        if access_token is not None:
            # print(access_token)
            return access_token
        else:
            raise ValidationError("Invalid credentials. Token hasn\'t been obtained")

    def generate_date_list(self, start_date=None, end_date=None):
        # converts a string into a datetime object
        to_date = lambda datetime: datetime.strftime(self.iso_format)
        start = datetime.strptime(start_date, self.iso_format)
        end = datetime.strptime(end_date, self.iso_format)

        # calculating number of days between two dates
        delta_days = (end - start).days

        date_list = [
            to_date(end - dt.timedelta(days=x))
            for x in range(delta_days + 1)
        ]

        return date_list

    def generate_between_date_minus_days_and_anoth_date(self, minus_days=None,
                                                        delta_days=None):

        today = datetime.today()
        # get time within gap
        corrected_tm = today - dt.timedelta(days=minus_days)

        # 2nd way ge time within 2 days
        to_date = lambda datetime: datetime.strftime(self.iso_format)

        date_list = [
            to_date(corrected_tm - dt.timedelta(days=x))
            for x in range(delta_days)
        ]

        return date_list

    def generate_between_now_minus_days(self, delta_days=None):
        to_date = lambda datetime: datetime.strftime(self.iso_format)
        today = datetime.today()

        # get dates within gap
        date_list = [
            to_date(today - dt.timedelta(days=x))
            for x in range(delta_days)
        ]
        return date_list

    def get_response_by_load_date(self):
        start_time = datetime.now()

        headers = {
            'Authorization': "Bearer " + self.get_token()
        }

        date_list = self.generate_date_list(self.start_date, self.end_date)
        print(date_list)
        # sends request to endpoint through the list comprehension for each date
        responses = [
           requests.request("GET", self.url, headers=headers, params={"LoadDate": date})
           for date in date_list
        ]

        # check response status
        if not len(responses) == 0:
            random_resp = responses[0]
            print(f"Response status: {random_resp.status_code}")

        
        end_time = datetime.now()

        random_dt = datetime.strptime(date_list[0], self.iso_format)
        month = random_dt.month
        month = self.get_month_from_num(month)

        latency = (end_time - start_time).total_seconds()

        if latency is not None:
            self.latency = latency
            self.save_latency_data(month, latency)


    def get_response_by_load_date_and_timedelta_days(self):
        start_time = datetime.now()
        self.auth_header['Authorization'] = "Bearer " + self.get_token()
        date_list = self.generate_date_list(self.start_date, self.end_date)
        print(date_list)


        responses = [
           requests.request("GET", self.url, headers=self.auth_header,  params={"LoadDate": date, "Days": self.days})
           for date in date_list
        ]

        # check response status
        if not len(responses) == 0:
            random_resp = responses[0]
            print(f"Response status: {random_resp.status_code}")

        end_time = datetime.now()

        random_dt = datetime.strptime(date_list[0], self.iso_format)
        month = random_dt.month
        month = self.get_month_from_num(month)

        latency = (end_time - start_time).total_seconds()

        if latency is not None:
            self.latency = latency
            self.save_latency_data(month, latency)



if __name__ == "__main__":
    print("-------------------------------------Start-------------------------------------")
    instance = ProcessReport()
    print(instance.get_token())
    # instance.get_response_by_load_date()
    instance.get_response_by_load_date_and_timedelta_days()

    print(f"{instance.latency} sec")
    print(instance.latency_data)
    print("-------------------------------------End---------------------------------------")
