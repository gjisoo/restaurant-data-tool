from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001_create_restaurants"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "restaurants",

        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "management_no",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(length=200),
            nullable=False,
        ),

        sa.Column(
            "business_type",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "city",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "district",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "dong",
            sa.String(length=50),
            nullable=True,
        ),

        sa.Column(
            "road_address",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "public_coord_x",
            sa.Numeric(18, 9),
            nullable=True,
        ),

        sa.Column(
            "public_coord_y",
            sa.Numeric(18, 9),
            nullable=True,
        ),

        sa.Column(
            "status_code",
            sa.String(length=10),
            nullable=True,
        ),

        sa.Column(
            "status_name",
            sa.String(length=50),
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

        sa.UniqueConstraint(
            "management_no",
            name="uq_restaurants_management_no",
        ),
    )

    op.create_index(
        "ix_restaurants_name",
        "restaurants",
        ["name"],
    )

    op.create_index(
        "ix_restaurants_location",
        "restaurants",
        ["city", "district", "dong"],
    )

    op.create_index(
        "ix_restaurants_status_code",
        "restaurants",
        ["status_code"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_restaurants_status_code",
        table_name="restaurants",
    )

    op.drop_index(
        "ix_restaurants_location",
        table_name="restaurants",
    )

    op.drop_index(
        "ix_restaurants_name",
        table_name="restaurants",
    )

    op.drop_table("restaurants")