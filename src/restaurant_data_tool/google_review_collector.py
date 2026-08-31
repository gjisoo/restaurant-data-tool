from datetime import datetime

from restaurant_data_tool.database import get_connection
from restaurant_data_tool.google_places import search_places
from restaurant_data_tool.coordinates import to_wgs84
from restaurant_data_tool.restaurant_matcher import find_best_match

def get_unmatched_restaurants():
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
                """
            )

            rows = cursor.fetchall()

    return rows

def save_google_place(
    cursor,
    restaurant_id: int,
    place: dict,
    match: dict,
) -> None:
    google_place_id = place.get("id")
    google_name = (
        place.get("displayName", {}).get("text")
    )

    rating = place.get("rating")
    review_count = place.get("userRatingCount")

    cursor.execute(
        """
        INSERT INTO restaurant_google_places (
            restaurant_id,
            google_place_id,
            google_name,
            rating,
            review_count,
            match_status,
            match_score,
            matched_at
        )
        VALUES (
            %(restaurant_id)s,
            %(google_place_id)s,
            %(google_name)s,
            %(rating)s,
            %(review_count)s,
            %(match_status)s,
            %(match_score)s,
            %(matched_at)s
        )
        ON CONFLICT (restaurant_id)
        DO UPDATE SET
            google_place_id = EXCLUDED.google_place_id,
            google_name = EXCLUDED.google_name,
            rating = EXCLUDED.rating,
            review_count = EXCLUDED.review_count,
            match_status = EXCLUDED.match_status,
            match_score = EXCLUDED.match_score,
            matched_at = EXCLUDED.matched_at,
            updated_at = NOW()
        """,
        {
            "restaurant_id": restaurant_id,
            "google_place_id": google_place_id,
            "google_name": google_name,
            "rating": rating,
            "review_count": review_count,
            "match_status": match["match_status"],
            "match_score": match["match_score"],
            "matched_at": datetime.now(),
        },
    )

def save_match_log(
    cursor,
    restaurant_id: int,
    status: str,
    candidate_count: int = 0,
    google_place_id: str | None = None,
    match_score: float | None = None,
    error_message: str | None = None,
) -> None:
    cursor.execute(
        """
        INSERT INTO restaurant_google_match_logs (
            restaurant_id,
            status,
            candidate_count,
            google_place_id,
            match_score,
            error_message
        )
        VALUES (
            %(restaurant_id)s,
            %(status)s,
            %(candidate_count)s,
            %(google_place_id)s,
            %(match_score)s,
            %(error_message)s
        )
        """,
        {
            "restaurant_id": restaurant_id,
            "status": status,
            "candidate_count": candidate_count,
            "google_place_id": google_place_id,
            "match_score": match_score,
            "error_message": error_message,
        },
    )

def main():
    restaurants = get_unmatched_restaurants()

    for restaurant in restaurants:
        (
            restaurant_id,
            name,
            road_address,
            public_coord_x,
            public_coord_y,
        ) = restaurant

        try:
            latitude, longitude = to_wgs84(
                public_coord_x,
                public_coord_y,
            )

            if latitude is None or longitude is None:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        save_match_log(
                            cursor=cursor,
                            restaurant_id=restaurant_id,
                            status="no_coordinates",
                        )
                        conn.commit()

                continue

            places = search_places(
                name=name,
                latitude=latitude,
                longitude=longitude,
            )

            best_match = find_best_match(
                public_name=name,
                public_address=road_address,
                public_latitude=latitude,
                public_longitude=longitude,
                places=places,
            )

            if best_match is None:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        save_match_log(
                            cursor=cursor,
                            restaurant_id=restaurant_id,
                            status="not_found",
                            candidate_count=len(places),
                        )
                        conn.commit()

                continue

            place = best_match["place"]
            match = best_match["match"]

            with get_connection() as conn:
                with conn.cursor() as cursor:
                    save_google_place(
                        cursor=cursor,
                        restaurant_id=restaurant_id,
                        place=place,
                        match=match,
                    )

                    save_match_log(
                        cursor=cursor,
                        restaurant_id=restaurant_id,
                        status="matched",
                        candidate_count=len(places),
                        google_place_id=place.get("id"),
                        match_score=match["match_score"],
                    )

                    conn.commit()

        except Exception as e:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    save_match_log(
                        cursor=cursor,
                        restaurant_id=restaurant_id,
                        status="error",
                        error_message=str(e),
                    )
                    conn.commit()


if __name__ == "__main__":
    main()