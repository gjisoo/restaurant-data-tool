from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004_google_match_logs"
down_revision = "003_reviews"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "restaurant_google_match_logs",

        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),

        # 어떤 공공데이터 식당에 대한 매칭 시도였는지
        sa.Column(
            "restaurant_id",
            sa.BigInteger(),
            sa.ForeignKey(
                "restaurants.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        # matched / not_found / no_coordinates / error
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),

        # Google 검색 결과 후보 개수
        sa.Column(
            "candidate_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        # 매칭 성공한 경우 Google Place ID
        sa.Column(
            "google_place_id",
            sa.String(length=255),
            nullable=True,
        ),

        # 매칭 성공 시 점수
        sa.Column(
            "match_score",
            sa.Numeric(5, 4),
            nullable=True,
        ),

        # 오류 발생 시 메시지
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),

        # 실제 처리 시각
        sa.Column(
            "processed_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_google_match_logs_restaurant_id",
        "restaurant_google_match_logs",
        ["restaurant_id"],
    )

    op.create_index(
        "ix_google_match_logs_status",
        "restaurant_google_match_logs",
        ["status"],
    )

    op.create_index(
        "ix_google_match_logs_processed_at",
        "restaurant_google_match_logs",
        ["processed_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_google_match_logs_processed_at",
        table_name="restaurant_google_match_logs",
    )

    op.drop_index(
        "ix_google_match_logs_status",
        table_name="restaurant_google_match_logs",
    )

    op.drop_index(
        "ix_google_match_logs_restaurant_id",
        table_name="restaurant_google_match_logs",
    )

    op.drop_table("restaurant_google_match_logs")