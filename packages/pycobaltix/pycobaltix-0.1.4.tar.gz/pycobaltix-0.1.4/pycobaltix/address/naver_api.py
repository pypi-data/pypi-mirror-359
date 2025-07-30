import requests

from pycobaltix.address.convert_coordinate import (
    tm128_to_wgs84,
    wgs84_to_tm128,
)
from pycobaltix.address.endpoint import NaverEndpoint
from pycobaltix.address.model import ConvertedCoordinate, NaverAddress


class NaverAPI:
    def __init__(self, api_key_id: str, api_key: str):
        self.api_key_id = api_key_id
        self.api_key = api_key

    def convert_address(self, address: str) -> ConvertedCoordinate | None:
        try:
            if len(address.replace(" ", "")) == 0:
                return None
            url = f"{NaverEndpoint.geocoding.value}?query={address}"
            response = requests.get(
                url,
                {
                    "X-NCP-APIGW-API-KEY-ID": self.api_key_id,
                    "X-NCP-APIGW-API-KEY": self.api_key,
                },
            )
            json_data = response.json()
            # transformed_elements를 딕셔너리로 변경
            if len(json_data.get("addresses")) == 0:
                print(address)
                return None
            transformed_elements_dict = {
                element["types"][0]: {  # 첫 번째 타입을 키로 사용
                    "longName": element["longName"],
                    "shortName": element["shortName"],
                }
                for element in json_data["addresses"][0]["addressElements"]
            }
            wgs84_x = json_data.get("addresses")[0].get("x")
            wgs84_y = json_data.get("addresses")[0].get("y")
            coordinates = wgs84_to_tm128(wgs84_x, wgs84_y)
            return ConvertedCoordinate(
                tm128_coordinate=coordinates,
                wgs84_coordinate=tm128_to_wgs84(
                    wgs84_x,
                    wgs84_y,
                ),
                transformed_elements=NaverAddress(transformed_elements_dict),
            )
        except Exception as e:
            print(e)
            return None
