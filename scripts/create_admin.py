"""Bootstrap the first admin user. There is no public signup endpoint by design.

Usage:
    python -m scripts.create_admin --email admin@example.com --name "Admin" --password secret
"""

import argparse
import sys

from app.core.security import hash_password
from app.crud.user import get_user_by_email
from app.db.session import SessionLocal
from app.models.enums import UserRole
from app.models.user import User


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    with SessionLocal() as db:
        if get_user_by_email(db, args.email) is not None:
            print(f"User {args.email} already exists.", file=sys.stderr)
            raise SystemExit(1)

        user = User(
            email=args.email,
            full_name=args.name,
            hashed_password=hash_password(args.password),
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        print(f"Created admin user {user.email} ({user.id})")


if __name__ == "__main__":
    main()
