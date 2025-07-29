import os
import requests
import xmltodict
from typing import List, Dict

class GeoReport:
    def __init__(self, root_address: str, jurisdiction: str = None, api_key: str = None, output_format: str = 'json') -> None:
        self.root_address = root_address.rstrip('/')
        self.jurisdiction = jurisdiction
        self.api_key = api_key or os.getenv('GEOREPORT_API_KEY')
        self.output_format = output_format

    def get_service_list(self) -> List[Dict]:
        params = {}
        if self.jurisdiction:
            params['jurisdiction_id'] = self.jurisdiction

        response = requests.get(f'{self.root_address}/services.{self.output_format}', params=params)
        response.raise_for_status()

        if self.output_format == 'json':
            return response.json()
        else:
            return xmltodict.parse(response.content)['services']['service']

    def get_service_definition(self, service_code: str) -> Dict:
        params = {}
        if self.jurisdiction:
            params['jurisdiction_id'] = self.jurisdiction
        
        response = requests.get(f'{self.root_address}/services/{service_code}.{self.output_format}', params=params)
        response.raise_for_status()

        if self.output_format == 'json':
            return response.json()
        else:
            return xmltodict.parse(response.content)['service_definition']
    
    def get_service_requests(self, service_request_id: str = None, start_date: str = None, end_date: str = None, status: str = None) -> List[Dict]:
        params = {}
        if service_request_id:
            params['service_request_id'] = service_request_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if status:
            params['status'] = status
        if self.jurisdiction:
            params['jurisdiction_id'] = self.jurisdiction

        response = requests.get(f'{self.root_address}/requests.{self.output_format}', params=params)
        response.raise_for_status()

        if self.output_format == 'json':
            return response.json()
        else:
            return xmltodict.parse(response.content)['service_requests']['request']
    
    def get_service_request(self, service_request_id: str) -> Dict:
        params = {}
        if self.jurisdiction:
            params['jurisdiction_id'] = self.jurisdiction

        response = requests.get(f'{self.root_address}/requests/{service_request_id}.{self.output_format}', params=params)
        response.raise_for_status()

        if self.output_format == 'json':
            return response.json()[0]
        else:
            return xmltodict.parse(response.content)['service_requests']['request']
