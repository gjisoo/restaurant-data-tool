from datetime import datetime

from restaurant_data_tool.database import get_connection
from restaurant_data_tool.google.places import (
    get_place_details,
    normalize_review,
)


def get_google_places():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    restaurant_id,
                    google_place_id
                FROM restaurant_google_places
                WHERE google_place_id IS NOT NULL
                    AND review_count > 0
                ORDER BY id
                """
            )

            return cursor.fetchall()


def save_review(
    cursor,
    restaurant_google_place_id: int,
    review: dict,
) -> None:
    cursor.execute(
        """
        INSERT INTO restaurant_google_reviews (
            restaurant_google_place_id,
            google_review_name,
            author_name,
            content,
            original_content,
            language_code,
            published_at,
            google_maps_uri
        )
        VALUES (
            %(restaurant_google_place_id)s,
            %(google_review_name)s,
            %(author_name)s,
            %(content)s,
            %(original_content)s,
            %(language_code)s,
            %(published_at)s,
            %(google_maps_uri)s
        )
        ON CONFLICT (google_review_name)
        DO UPDATE SET
            author_name = EXCLUDED.author_name,
            content = EXCLUDED.content,
            original_content = EXCLUDED.original_content,
            language_code = EXCLUDED.language_code,
            published_at = EXCLUDED.published_at,
            google_maps_uri = EXCLUDED.google_maps_uri,
            updated_at = NOW()
        """,
        {
            "restaurant_google_place_id": restaurant_google_place_id,
            **review,
        },
    )


def main():
    google_places = get_google_places()

    for google_place in google_places:
        (
            restaurant_google_place_id,
            restaurant_id,
            google_place_id,
        ) = google_place

        try:
            place = get_place_details(
                google_place_id
            )

            reviews = place.get("reviews", [])

            print(
                f"[INFO] restaurant_id={restaurant_id}, "
                f"google_place_id={google_place_id}, "
                f"reviews={len(reviews)}"
            )

            with get_connection() as conn:
                with conn.cursor() as cursor:
                    for review in reviews:
                        normalized_review = normalize_review(
                            review
                        )

                        save_review(
                            cursor=cursor,
                            restaurant_google_place_id=(
                                restaurant_google_place_id
                            ),
                            review=normalized_review,
                        )

                    cursor.execute(
                        """
                        UPDATE restaurant_google_places
                        SET
                            review_count = %(review_count)s,
                            updated_at = NOW()
                        WHERE id = %(id)s
                        """,
                        {
                            "review_count": place.get(
                                "userRatingCount"
                            ),
                            "id": restaurant_google_place_id,
                        },
                    )

                    conn.commit()

                    print(
                        f"[SUCCESS] restaurant_id={restaurant_id} 저장 완료"
                    )

        except Exception as e:
            print(
                f"[ERROR] restaurant_id={restaurant_id}, "
                f"google_place_id={google_place_id}, "
                f"error={e}"
            )


if __name__ == "__main__":
    main()