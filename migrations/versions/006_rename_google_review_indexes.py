from alembic import op


# revision identifiers, used by Alembic.
revision = "006_rename_google_review_indexes"
down_revision = "005_rename_google_reviews"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER INDEX ix_restaurant_reviews_google_place_id
        RENAME TO ix_restaurant_google_reviews_google_place_id
        """
    )

    op.execute(
        """
        ALTER INDEX ix_restaurant_reviews_published_at
        RENAME TO ix_restaurant_google_reviews_published_at
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER INDEX ix_restaurant_google_reviews_google_place_id
        RENAME TO ix_restaurant_reviews_google_place_id
        """
    )

    op.execute(
        """
        ALTER INDEX ix_restaurant_google_reviews_published_at
        RENAME TO ix_restaurant_reviews_published_at
        """
    )