from restaurant_data_tool.database import get_connection
from restaurant_data_tool.google_places import search_places
from restaurant_data_tool.coordinates import to_wgs84

def get_unmatched_restaurants(limit=5):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    r.id,
                    r.name,
                    r.road_address,
                    r.public_coord_x,
                    r.public_coord_y
                FROM restaurants r
                LEFT JOIN restaurant_google_places rgp
                    ON rgp.restaurant_id = r.id
                WHERE rgp.id IS NULL
                ORDER BY r.id
                LIMIT %s
                """,
                (limit,),
            )

            rows = cursor.fetchall()

    return rows


def main():
    restaurants = get_unmatched_restaurants(limit=5)

    for restaurant in restaurants:
        (
            restaurant_id,
            name,
            road_address,
            public_coord_x,
            public_coord_y,
        ) = restaurant

        print()
        print("=" * 50)
        print(f"restaurant_id: {restaurant_id}")
        print(f"name: {name}")
        print(f"address: {road_address}")

        latitude, longitude = to_wgs84(
            public_coord_x,
            public_coord_y,
        )

        print(f"converted latitude: {latitude}")
        print(f"converted longitude: {longitude}")

        places = search_places(
            name=name,
            latitude=latitude,
            longitude=longitude,
        )

        print(f"Google 검색 후보 수: {len(places)}")

        for index, place in enumerate(places, start=1):
            print()
            print(f"[후보 {index}]")
            print(
                "Google Place ID:",
                place.get("id"),
            )
            print(
                "이름:",
                place.get("displayName", {}).get("text"),
            )
            print(
                "주소:",
                place.get("formattedAddress"),
            )
            print(
                "위도:",
                place.get("location", {}).get("latitude"),
            )
            print(
                "경도:",
                place.get("location", {}).get("longitude"),
            )
            print(
                "평점:",
                place.get("rating"),
            )
            print(
                "리뷰 수:",
                place.get("userRatingCount"),
            )

if __name__ == "__main__":
    main()