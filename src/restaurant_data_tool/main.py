import os
from decimal import Decimal

import requests
from dotenv import load_dotenv

from restaurant_data_tool.database import get_connection


load_dotenv()


SERVICE_KEY = os.getenv("DATA_GO_KR_SERVICE_KEY")

BASE_URL = "https://apis.data.go.kr/1741000/general_restaurants/info"
SEOUL_GEUMCHEON_QUERY = "서울특별시 금천구"
OPEN_STATUS = "영업/정상"
KOREAN_SUFFIXES = ("동", "읍", "면")


def fetch_restaurants(page_no=1, num_of_rows=100):
    url = f"{BASE_URL}?serviceKey={SERVICE_KEY}"

    params = {
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "returnType": "json",
        "cond[ROAD_NM_ADDR::LIKE]": SEOUL_GEUMCHEON_QUERY,
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def parse_address(item):
    address = item.get("LOTNO_ADDR") or item.get("ROAD_NM_ADDR") or ""

    parts = address.split()

    city = parts[0] if len(parts) >= 1 else None
    district = parts[1] if len(parts) >= 2 else None

    dong = None

    for part in parts:
        if part.endswith(KOREAN_SUFFIXES):
            dong = part
            break

    return city, district, dong


def to_decimal(value):
    if value is None or value == "":
        return None

    return Decimal(value)


def save_restaurant(cursor, item):
    city, district, dong = parse_address(item)

    cursor.execute(
        """
        INSERT INTO restaurants (
            management_no,
            name,
            business_type,
            city,
            district,
            dong,
            road_address,
            public_coord_x,
            public_coord_y,
            status_code,
            status_name
        )
        VALUES (
            %(management_no)s,
            %(name)s,
            %(business_type)s,
            %(city)s,
            %(district)s,
            %(dong)s,
            %(road_address)s,
            %(public_coord_x)s,
            %(public_coord_y)s,
            %(status_code)s,
            %(status_name)s
        )
        ON CONFLICT (management_no)
        DO NOTHING
        RETURNING 1
        """,
        {
            "management_no": item.get("MNG_NO"),
            "name": item.get("BPLC_NM"),
            "business_type": item.get("SNTTN_BZSTAT_NM"),
            "city": city,
            "district": district,
            "dong": dong,
            "road_address": item.get("ROAD_NM_ADDR"),
            "public_coord_x": to_decimal(item.get("CRD_INFO_X")),
            "public_coord_y": to_decimal(item.get("CRD_INFO_Y")),
            "status_code": item.get("SALS_STTS_CD"),
            "status_name": item.get("SALS_STTS_NM"),
        },
    )

    return cursor.fetchone() is not None


def collect_restaurants():
    page_no = 1
    num_of_rows = 100

    total_saved = 0

    with get_connection() as conn:
        with conn.cursor() as cursor:
            while True:

                data = fetch_restaurants(
                    page_no=page_no,
                    num_of_rows=num_of_rows,
                )

                body = data["response"]["body"]

                items = body.get("items", {}).get("item", [])
                total_count = body["totalCount"]

                if not items:
                    break

                for item in items:
                    if item.get("SALS_STTS_NM") != OPEN_STATUS:
                        continue

                    if save_restaurant(cursor, item):
                        total_saved += 1

                conn.commit()

                if page_no * num_of_rows >= total_count:
                    break

                page_no += 1

def main():
    if not SERVICE_KEY:
        raise ValueError("DATA_GO_KR_SERVICE_KEY is not set.")

    collect_restaurants()


if __name__ == "__main__":
    main()
