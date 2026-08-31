from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002_google_places"
down_revision = "001_create_restaurants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "restaurant_google_places",

        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),

        # restaurants 테이블의 식당 ID
        sa.Column(
            "restaurant_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "restaurants.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        # Google Places의 고유 Place ID
        sa.Column(
            "google_place_id",
            sa.String(length=255),
            nullable=False,
        ),

        # Google에 등록되어 있는 식당명
        sa.Column(
            "google_name",
            sa.String(length=200),
            nullable=True,
        ),

        # Google 평균 평점 (예: 4.3)
        sa.Column(
            "rating",
            sa.Numeric(3, 2),
            nullable=True,
        ),

        # Google 전체 리뷰 수
        sa.Column(
            "review_count",
            sa.Integer(),
            nullable=True,
        ),

        # matched / needs_review 등 매칭 상태
        sa.Column(
            "match_status",
            sa.String(length=30),
            nullable=False,
        ),

        # 공공데이터와 Google 식당의 매칭 신뢰도
        # 0.0000 ~ 1.0000
        sa.Column(
            "match_score",
            sa.Numeric(5, 4),
            nullable=True,
        ),

        # Google 식당과 매칭된 시각
        sa.Column(
            "matched_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),

        # 하나의 공공데이터 식당에는 Google 장소 하나만 연결
        sa.UniqueConstraint(
            "restaurant_id",
            name="uq_restaurant_google_places_restaurant_id",
        ),

        # 동일한 Google 장소가 여러 식당에 중복 연결되는 것 방지
        sa.UniqueConstraint(
            "google_place_id",
            name="uq_restaurant_google_places_google_place_id",
        ),
    )

    op.create_index(
        "ix_restaurant_google_places_match_status",
        "restaurant_google_places",
        ["match_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_restaurant_google_places_match_status",
        table_name="restaurant_google_places",
    )

    op.drop_table("restaurant_google_places")