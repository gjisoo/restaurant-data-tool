import os
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

BASE_URL = "https://places.googleapis.com/v1"


if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY is not set.")


def search_places(
    name: str,
    latitude: float | None = None,
    longitude: float | None = None,
    max_result_count: int = 5,
):
    url = f"{BASE_URL}/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.rating,"
            "places.userRatingCount"
        ),
    }

    body = {
        "textQuery": name,
        "languageCode": "ko",
        "regionCode": "KR",
        "pageSize": max_result_count,
    }

    if latitude is not None and longitude is not None:
        body["locationBias"] = {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": 100.0,
            }
        }

    response = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=15,
    )

    response.raise_for_status()

    return response.json().get("places", [])


def get_place_details(
    google_place_id: str,
) -> dict[str, Any]:
    """
    Google Place ID로 식당 상세정보와 리뷰를 가져온다.
    """

    url = f"{BASE_URL}/places/{google_place_id}"

    headers = {
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": (
            "id,"
            "displayName,"
            "rating,"
            "userRatingCount,"
            "reviews"
        ),
    }

    params = {
        "languageCode": "ko",
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


def get_reviews(
    google_place_id: str,
) -> list[dict[str, Any]]:
    """
    Google Place ID에 해당하는 리뷰 목록만 반환한다.
    """

    place = get_place_details(google_place_id)

    return place.get("reviews", [])


def normalize_review(
    review: dict[str, Any],
) -> dict[str, Any]:
    """
    Google 리뷰 데이터를 restaurant_reviews 테이블에
    저장하기 쉬운 형태로 변환한다.
    """

    author = review.get("authorAttribution") or {}
    text = review.get("text") or {}
    original_text = review.get("originalText") or {}

    return {
        "author_name": author.get("displayName"),
        "rating": review.get("rating"),
        "content": text.get("text"),
        "original_content": original_text.get("text"),
        "language_code": (
            original_text.get("languageCode")
            or text.get("languageCode")
        ),
        "published_at": review.get("publishTime"),
    }