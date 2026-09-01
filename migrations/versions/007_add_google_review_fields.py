from alembic import op
import sqlalchemy as sa


revision = "007_add_google_review_fields"
down_revision = "006_rename_google_review_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "restaurant_google_reviews",
        sa.Column(
            "google_review_name",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.add_column(
        "restaurant_google_reviews",
        sa.Column(
            "google_maps_uri",
            sa.Text(),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_restaurant_google_reviews_google_review_name",
        "restaurant_google_reviews",
        ["google_review_name"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_restaurant_google_reviews_google_review_name",
        "restaurant_google_reviews",
        type_="unique",
    )

    op.drop_column(
        "restaurant_google_reviews",
        "google_maps_uri",
    )

    op.drop_column(
        "restaurant_google_reviews",
        "google_review_name",
    )