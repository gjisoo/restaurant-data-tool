from alembic import op


# revision identifiers, used by Alembic.
revision = "005_rename_google_reviews"
down_revision = "004_google_match_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Google 리뷰와 자체 서비스 리뷰를 구분하기 위해
    기존 restaurant_reviews 테이블을
    restaurant_google_reviews로 변경한다.
    """

    op.rename_table(
        "restaurant_reviews",
        "restaurant_google_reviews",
    )


def downgrade() -> None:
    """
    restaurant_google_reviews 테이블을
    기존 restaurant_reviews 이름으로 되돌린다.
    """

    op.rename_table(
        "restaurant_google_reviews",
        "restaurant_reviews",
    )