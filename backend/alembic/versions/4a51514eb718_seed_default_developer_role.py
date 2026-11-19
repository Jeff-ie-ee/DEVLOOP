
"""seed default developer role

Revision ID: 4a51514eb718
Revises: d5a46f6bb6fa
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4a51514eb718"
down_revision: str | Sequence[str] | None = "d5a46f6bb6fa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


roles = sa.table(
    "roles",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String(50)),
    sa.column("description", sa.String(255)),
)

user_roles = sa.table(
    "user_roles",
    sa.column("role_id", sa.Integer),
    sa.column("user_id", sa.Integer),
)


def upgrade() -> None:
    """Create the default developer role if it does not exist."""

    connection = op.get_bind()

    existing_role = connection.execute(
        sa.select(roles.c.id).where(
            roles.c.name == "developer"
        )
    ).scalar_one_or_none()

    if existing_role is None:
        connection.execute(
            roles.insert().values(
                name="developer",
                description="Standard DEVLOOP developer",
            )
        )


def downgrade() -> None:
    """Remove the developer role only when it is not assigned."""

    connection = op.get_bind()

    role_id = connection.execute(
        sa.select(roles.c.id).where(
            roles.c.name == "developer"
        )
    ).scalar_one_or_none()

    if role_id is None:
        return

    assignment_exists = connection.execute(
        sa.select(user_roles.c.role_id)
        .where(user_roles.c.role_id == role_id)
        .limit(1)
    ).first()

    if assignment_exists is not None:
        raise RuntimeError(
            "Cannot remove the developer role while it is assigned to users."
        )

    connection.execute(
        roles.delete().where(roles.c.id == role_id)
    )
