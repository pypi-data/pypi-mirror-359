import requests
from typing import Callable

class HttpDataSource:
    
    @staticmethod
    def base_process_function(host: str, endpoint: str) -> dict:
        response = requests.get(f"{host}/{endpoint}")
        response.raise_for_status()
        return response.json()
    
    
    def __init__(self, host, endpoint,process_function: Callable[[str, str], dict] = None):
            self.host = host
            self.endpoint = endpoint
            self.process_function = process_function or self.base_process_function


    def get(self):
        """
        Fetch data from the specified host and endpoint using the process function.
        
        :param host: The base URL of the API.
        :param endpoint: The specific endpoint to fetch data from.
        :return: Processed data from the API.
        """
        return self.process_function(self.host, self.endpoint)