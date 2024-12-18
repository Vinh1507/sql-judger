import requests
import os

class ApiHelper:
    def __init__(self):
        self.base_url = os.getenv('SQL_LAB_SERVER_BASE_URL')
        token = os.getenv('SQL_JUDGER_SERVICE_TOKEN')
        # Set the headers with the Bearer token
        headers = {
            'Authorization': f'Bearer {token}',
        }
        self.headers = headers

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Assuming the response is in JSON format
        except requests.exceptions.RequestException as e:
            print(f"GET request failed: {e}")
            return None

    def post(self, endpoint, json_data):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, json=json_data, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Assuming the response is in JSON format
        except requests.exceptions.RequestException as e:
            print(f"POST request failed: {e}")
            return None