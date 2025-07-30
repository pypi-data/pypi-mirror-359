from typing import Any, Dict

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

    def _reverse_geocoding(self, x: float, y: float) -> Dict[str, Any] | None:
        """역 지오코딩을 통해 좌표에서 지역 정보를 가져옵니다."""
        url = f"{NaverEndpoint.reverse_geocoding.value}?coords={x},{y}"
        response = requests.get(
            url,
            headers={
                "X-NCP-APIGW-API-KEY-ID": self.api_key_id,
                "X-NCP-APIGW-API-KEY": self.api_key,
            },
        )
        response.raise_for_status()

        json_data = response.json()

        # 응답 상태 확인
        if json_data.get("status", {}).get("code") != 0:
            return None

        # results 배열에서 첫 번째 항목 추출
        results = json_data.get("results", [])
        if not results:
            return None

        first_result = results[0]

        # 필요한 정보 추출
        return {
            "pnu": first_result.get("code", {}).get("id"),
            "area1": first_result.get("region", {})
            .get("area1", {})
            .get("name"),  # 시/도
            "area2": first_result.get("region", {})
            .get("area2", {})
            .get("name"),  # 시/군/구
            "area3": first_result.get("region", {})
            .get("area3", {})
            .get("name"),  # 읍/면/동
            "area4": first_result.get("region", {}).get("area4", {}).get("name"),  # 리
        }

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
            reverse_geocoding_data = self._reverse_geocoding(wgs84_x, wgs84_y)
            coordinates = wgs84_to_tm128(wgs84_x, wgs84_y)
            naver_address = NaverAddress(transformed_elements_dict)
            naver_address.pnu = (
                reverse_geocoding_data.get("pnu") if reverse_geocoding_data else None
            )
            return ConvertedCoordinate(
                tm128_coordinate=coordinates,
                wgs84_coordinate=tm128_to_wgs84(
                    wgs84_x,
                    wgs84_y,
                ),
                transformed_elements=naver_address,
            )
        except Exception as e:
            print(e)
            return None
