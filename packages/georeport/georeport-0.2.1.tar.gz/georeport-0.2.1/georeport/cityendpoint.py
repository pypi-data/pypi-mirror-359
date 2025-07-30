from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class CityEndpoint:
    name: str
    root_address: str
    jurisdiction: Optional[str] = None


class CityEndpoints:
    _cities: Dict[str, CityEndpoint] = {
        'Bloomington, IN': CityEndpoint(
            name='Bloomington, IN',
            root_address='https://bloomington.in.gov/crm/open311/v2'
        ),
        'Brookline, MA': CityEndpoint(
            name='Brookline, MA',
            root_address='https://spot.brooklinema.gov/open311/v2'
        ),
        'Chicago, IL': CityEndpoint(
            name='Chicago, IL',
            root_address='http://311api.cityofchicago.org/open311/v2'
        ),
    }

    @classmethod
    def list_city_keys(cls) -> List[str]:
        return list(cls._cities.keys())

    @classmethod
    def get(cls, city_key: str) -> CityEndpoint:
        return cls._cities[city_key]
