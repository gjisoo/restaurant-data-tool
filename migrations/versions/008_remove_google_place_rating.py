from alembic import op
import sqlalchemy as sa


revision = "008_remove_google_place_rating"
down_revision = "007_add_google_review_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column(
        "restaurant_google_places",
        "rating",
    )


def downgrade() -> None:
    op.add_column(
        "restaurant_google_places",
        sa.Column(
            "rating",
            sa.Numeric(precision=3, scale=2),
            nullable=True,
        ),
    )