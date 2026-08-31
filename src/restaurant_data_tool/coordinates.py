from decimal import Decimal

from pyproj import Transformer


# 공공데이터 좌표계 (EPSG:5174)
# → Google Maps에서 사용하는 WGS84 (EPSG:4326)
_TO_WGS84 = Transformer.from_crs(
    "EPSG:5174",
    "EPSG:4326",
    always_xy=True,
)


def to_wgs84(
    x: Decimal | float | None,
    y: Decimal | float | None,
) -> tuple[float | None, float | None]:
    """
    공공데이터의 EPSG:5174 X/Y 좌표를
    WGS84 위도/경도로 변환한다.

    Returns:
        (latitude, longitude)
    """

    if x is None or y is None:
        return None, None

    longitude, latitude = _TO_WGS84.transform(
        float(x),
        float(y),
    )

    return latitude, longitude