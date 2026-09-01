from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "009_remove_google_review_rating"
down_revision = "008_remove_google_place_rating"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column(
        "restaurant_google_reviews",
        "rating",
    )


def downgrade() -> None:
    op.add_column(
        "restaurant_google_reviews",
        sa.Column(
            "rating",
            sa.Numeric(precision=3, scale=2),
            nullable=True,
        ),
    )