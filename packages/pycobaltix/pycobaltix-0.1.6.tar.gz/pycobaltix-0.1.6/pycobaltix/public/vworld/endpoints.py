import math
import os
from abc import ABC, abstractmethod
from typing import Any, Dict

import httpx

from pycobaltix.public.vworld.response.buldSnList import BuildingInfo
from pycobaltix.public.vworld.response.ladfrlList import LandInfo
from pycobaltix.public.vworld.response_format import ResponseFormat
from pycobaltix.schemas.responses import PaginatedAPIResponse, PaginationInfo


class BaseVWorldAPI(ABC):
    """V-World API의 공통 로직을 담은 베이스 클래스"""

    def __init__(self, api_key: str | None = None, domain: str | None = None):
        self.api_key = api_key or os.getenv("VWORLD_API_KEY")
        self.domain = domain or os.getenv("VWORLD_DOMAIN")
        if not self.api_key:
            raise ValueError("VWORLD_API_KEY 환경 변수가 설정되지 않았습니다")
        if not self.domain:
            raise ValueError("VWORLD_DOMAIN 환경 변수가 설정되지 않았습니다")
        self.base_url = "https://api.vworld.kr"

    def _prepare_params(self, **params) -> Dict[str, Any]:
        """요청 파라미터 준비 (공통 로직)"""
        # 모든 요청에 key, domain 자동 추가
        params.update({"key": self.api_key, "domain": self.domain})
        params.update({"format": ResponseFormat.JSON.value})

        # None 값과 빈 문자열 제거
        return {k: v for k, v in params.items() if v is not None and v != ""}

    def _parse_building_response(
        self, response: Dict[str, Any], numOfRows: int, pageNo: int
    ) -> PaginatedAPIResponse[BuildingInfo]:
        """건물 관련 응답 파싱 (공통 로직)"""
        if "ldaregVOList" not in response:
            return PaginatedAPIResponse(
                data=[],
                pagination=PaginationInfo(
                    currentPage=1,
                    totalPages=1,
                    totalCount=0,
                    count=0,
                    hasNext=False,
                    hasPrevious=False,
                ),
            )

        total_count = int(response["ldaregVOList"]["totalCount"])
        total_pages = math.ceil(total_count / numOfRows)
        current_page = int(response["ldaregVOList"]["pageNo"])

        pagination = PaginationInfo(
            currentPage=current_page,
            totalPages=total_pages,
            totalCount=total_count,
            count=numOfRows,
            hasNext=current_page < total_pages,
            hasPrevious=current_page > 1,
        )

        return PaginatedAPIResponse(
            success=True,
            message="success",
            status=200,
            data=[
                BuildingInfo.from_dict(item)
                for item in response["ldaregVOList"]["ldaregVOList"]
            ],
            pagination=pagination,
        )

    def _parse_land_response(
        self, response: Dict[str, Any], numOfRows: int, pageNo: int
    ) -> PaginatedAPIResponse[LandInfo]:
        """땅 관련 응답 파싱 (공통 로직)"""
        if "ladfrlVOList" not in response:
            return PaginatedAPIResponse(
                data=[],
                pagination=PaginationInfo(
                    currentPage=1,
                    totalPages=1,
                    totalCount=0,
                    count=0,
                    hasNext=False,
                    hasPrevious=False,
                ),
            )

        total_count = int(response["ladfrlVOList"]["totalCount"])
        total_pages = math.ceil(total_count / numOfRows)
        current_page = int(response["ladfrlVOList"]["pageNo"])

        pagination = PaginationInfo(
            currentPage=current_page,
            totalPages=total_pages,
            totalCount=total_count,
            count=numOfRows,
            hasNext=current_page < total_pages,
            hasPrevious=current_page > 1,
        )

        return PaginatedAPIResponse(
            success=True,
            message="success",
            status=200,
            data=[
                LandInfo.from_dict(item)
                for item in response["ladfrlVOList"]["ladfrlVOList"]
            ],
            pagination=pagination,
        )

    @abstractmethod
    def _make_request(self, endpoint: str, **params) -> Dict[str, Any]:
        """HTTP 요청 실행 (동기/비동기에서 각각 구현)"""
        pass


class VWorldAPI(BaseVWorldAPI):
    """V-World API 동기 클라이언트"""

    def _make_request(self, endpoint: str, **params) -> Dict[str, Any]:
        """동기 HTTP 요청"""
        filtered_params = self._prepare_params(**params)
        url = f"{self.base_url}{endpoint}"
        response = httpx.get(url, params=filtered_params)
        response.raise_for_status()
        return response.json()

    def buldSnList(
        self,
        pnu: str,
        agbldgSn: str | None = None,
        numOfRows: int = 100,
        pageNo: int = 1,
    ) -> PaginatedAPIResponse[BuildingInfo]:
        """건물일련번호조회"""
        response = self._make_request(
            "/ned/data/buldSnList",
            pnu=pnu,
            agbldgSn=agbldgSn,
            numOfRows=numOfRows,
            pageNo=pageNo,
        )
        return self._parse_building_response(response, numOfRows, pageNo)

    def buldHoCoList(
        self,
        pnu: str,
        agbldgSn: str | None = None,
        buldDongNm: str | None = None,
        buldFloorNm: str | None = None,
        buldHoNm: str | None = None,
        numOfRows: int = 100,
        pageNo: int = 1,
    ) -> PaginatedAPIResponse[BuildingInfo]:
        """건물호수조회"""
        response = self._make_request(
            "/ned/data/buldHoCoList",
            pnu=pnu,
            agbldgSn=agbldgSn,
            buldDongNm=buldDongNm,
            buldFloorNm=buldFloorNm,
            buldHoNm=buldHoNm,
            numOfRows=numOfRows,
            pageNo=pageNo,
        )
        return self._parse_building_response(response, numOfRows, pageNo)

    def ladfrlList(
        self,
        pnu: str,
        numOfRows: int = 100,
        pageNo: int = 1,
    ) -> PaginatedAPIResponse[LandInfo]:
        """토지 임야 목록 조회"""
        response = self._make_request(
            "/ned/data/ladfrlList",
            pnu=pnu,
            numOfRows=numOfRows,
            pageNo=pageNo,
        )
        return self._parse_land_response(response, numOfRows, pageNo)


class AsyncVWorldAPI(BaseVWorldAPI):
    """V-World API 비동기 클라이언트"""

    async def _make_request(self, endpoint: str, **params) -> Dict[str, Any]:
        """비동기 HTTP 요청"""
        filtered_params = self._prepare_params(**params)
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=filtered_params)
            response.raise_for_status()
            return response.json()

    async def buldSnList(
        self,
        pnu: str,
        agbldgSn: str | None = None,
        numOfRows: int = 100,
        pageNo: int = 1,
    ) -> PaginatedAPIResponse[BuildingInfo]:
        """건물일련번호조회 (비동기)"""
        response = await self._make_request(
            "/ned/data/buldSnList",
            pnu=pnu,
            agbldgSn=agbldgSn,
            numOfRows=numOfRows,
            pageNo=pageNo,
        )
        return self._parse_building_response(response, numOfRows, pageNo)

    async def buldHoCoList(
        self,
        pnu: str,
        agbldgSn: str | None = None,
        buldDongNm: str | None = None,
        buldFloorNm: str | None = None,
        buldHoNm: str | None = None,
        numOfRows: int = 100,
        pageNo: int = 1,
    ) -> PaginatedAPIResponse[BuildingInfo]:
        """건물호수조회 (비동기)"""
        response = await self._make_request(
            "/ned/data/buldHoCoList",
            pnu=pnu,
            agbldgSn=agbldgSn,
            buldDongNm=buldDongNm,
            buldFloorNm=buldFloorNm,
            buldHoNm=buldHoNm,
            numOfRows=numOfRows,
            pageNo=pageNo,
        )
        return self._parse_building_response(response, numOfRows, pageNo)

    async def ladfrlList(
        self,
        pnu: str,
        numOfRows: int = 100,
        pageNo: int = 1,
    ) -> PaginatedAPIResponse[LandInfo]:
        """토지 임야 목록 조회"""
        response = await self._make_request(
            "/ned/data/ladfrlList",
            pnu=pnu,
            numOfRows=numOfRows,
            pageNo=pageNo,
        )
        return self._parse_land_response(response, numOfRows, pageNo)
