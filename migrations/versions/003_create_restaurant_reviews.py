from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003_reviews"
down_revision = "002_google_places"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "restaurant_reviews",

        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),

        # restaurant_google_places.id FK
        sa.Column(
            "restaurant_google_place_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "restaurant_google_places.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        # Google 리뷰 작성자 표시 이름
        sa.Column(
            "author_name",
            sa.String(length=200),
            nullable=True,
        ),

        # 리뷰 별점
        sa.Column(
            "rating",
            sa.Numeric(3, 2),
            nullable=True,
        ),

        # languageCode에 따라 반환된 리뷰 내용
        sa.Column(
            "content",
            sa.Text(),
            nullable=True,
        ),

        # Google에 실제 작성된 원문
        sa.Column(
            "original_content",
            sa.Text(),
            nullable=True,
        ),

        # ko, en, ja 등
        sa.Column(
            "language_code",
            sa.String(length=20),
            nullable=True,
        ),

        # Google 리뷰 게시 시각
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        # 우리 DB에 처음 저장된 시각
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),

        # 우리 DB에서 마지막으로 수정된 시각
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_restaurant_reviews_google_place_id",
        "restaurant_reviews",
        ["restaurant_google_place_id"],
    )

    op.create_index(
        "ix_restaurant_reviews_published_at",
        "restaurant_reviews",
        ["published_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_restaurant_reviews_published_at",
        table_name="restaurant_reviews",
    )

    op.drop_index(
        "ix_restaurant_reviews_google_place_id",
        table_name="restaurant_reviews",
    )

    op.drop_table("restaurant_reviews")