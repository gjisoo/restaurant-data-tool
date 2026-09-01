import re
from difflib import SequenceMatcher
from math import radians, sin, cos, sqrt, atan2


def normalize_name(name: str | None) -> str:
    if not name:
        return ""

    name = name.lower()
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"[^0-9a-z가-힣]", "", name)

    return name


def calculate_name_similarity(
    public_name: str,
    google_name: str,
) -> float:
    public_name = normalize_name(public_name)
    google_name = normalize_name(google_name)

    if not public_name or not google_name:
        return 0.0

    return SequenceMatcher(
        None,
        public_name,
        google_name,
    ).ratio()


def normalize_address(address: str | None) -> str:
    if not address:
        return ""

    address = address.lower()

    address = address.replace("대한민국", "")
    address = address.replace("서울특별시", "서울")

    # 괄호 안 상세 정보 제거
    address = re.sub(r"\([^)]*\)", "", address)

    # 쉼표 제거
    address = address.replace(",", " ")

    # 여러 공백 정리
    address = re.sub(r"\s+", " ", address)

    return address.strip()


def extract_road_address_key(
    address: str | None,
) -> str:
    """
    도로명 + 건물번호만 추출한다.

    예:
    서울특별시 금천구 시흥대로 291, 310동 151호
    -> 시흥대로 291

    서울특별시 금천구 독산로64길 25, 102호
    -> 독산로64길 25
    """

    if not address:
        return ""

    address = normalize_address(address)

    match = re.search(
        r"([가-힣0-9]+(?:대로|로|길))\s*(\d+(?:-\d+)?)",
        address,
    )

    if not match:
        return ""

    road_name = match.group(1)
    building_number = match.group(2)

    return f"{road_name} {building_number}"


def calculate_address_similarity(
    public_address: str | None,
    google_address: str | None,
) -> float:
    """
    핵심 도로명주소가 같으면 1.0.
    그렇지 않으면 전체 주소 문자열 유사도를 계산한다.
    """

    public_key = extract_road_address_key(public_address)
    google_key = extract_road_address_key(google_address)

    if public_key and google_key:
        if public_key == google_key:
            return 1.0

    public_normalized = normalize_address(public_address)
    google_normalized = normalize_address(google_address)

    if not public_normalized or not google_normalized:
        return 0.0

    return SequenceMatcher(
        None,
        public_normalized,
        google_normalized,
    ).ratio()


def calculate_distance_meters(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    두 위경도 사이 거리를 미터 단위로 계산한다.
    """

    earth_radius = 6371000

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return earth_radius * c


def match_place(
        
    public_name: str,
    public_address: str,
    public_latitude: float | None,
    public_longitude: float | None,
    place: dict,
) -> dict:
    google_name = (
        place.get("displayName", {}).get("text") or ""
    )

    google_address = place.get("formattedAddress") or ""

    location = place.get("location") or {}

    google_latitude = location.get("latitude")
    google_longitude = location.get("longitude")

    # 공공데이터 또는 Google 좌표가 없으면 매칭 불가
    if (
        public_latitude is None
        or public_longitude is None
        or google_latitude is None
        or google_longitude is None
    ):
        return {
            "matched": False,
            "match_status": "needs_review",
            "match_score": 0.0,
            "name_similarity": 0.0,
            "address_similarity": 0.0,
            "distance_meters": None,
        }

    name_similarity = calculate_name_similarity(
        public_name,
        google_name,
    )

    address_similarity = calculate_address_similarity(
        public_address,
        google_address,
    )

    distance_meters = calculate_distance_meters(
        public_latitude,
        public_longitude,
        google_latitude,
        google_longitude,
    )

    # 주소를 가장 중요하게 본다.
    # 주소 핵심 일치 + 거리 100m 이내 + 이름 유사도 0.7 이상
    matched = (
        address_similarity >= 0.8
        and distance_meters <= 100
        and name_similarity >= 0.7
    )

    # 거리 점수
    distance_score = max(
        0.0,
        1 - (distance_meters / 100),
    )

    # 주소 비중을 가장 높게 둔다.
    match_score = (
        address_similarity * 0.5
        + name_similarity * 0.35
        + distance_score * 0.15
    )

    if matched:
        match_status = "matched"
    else:
        match_status = "needs_review"

    return {
        "matched": matched,
        "match_status": match_status,
        "match_score": round(match_score, 4),
        "name_similarity": round(name_similarity, 4),
        "address_similarity": round(address_similarity, 4),
        "distance_meters": round(distance_meters, 2),
    }


def find_best_match(
    public_name: str,
    public_address: str,
    public_latitude: float | None,
    public_longitude: float,
    places: list[dict],
):
    """
    Google 검색 후보 중 가장 점수가 높은 후보를 반환한다.
    단, matched=True인 후보만 최종 매칭으로 인정한다.
    """

    candidates = []

    for place in places:
        result = match_place(
            public_name=public_name,
            public_address=public_address,
            public_latitude=public_latitude,
            public_longitude=public_longitude,
            place=place,
        )

        candidates.append(
            {
                "place": place,
                "match": result,
            }
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item["match"]["match_score"],
        reverse=True,
    )

    best = candidates[0]

    if not best["match"]["matched"]:
        return None

    return best