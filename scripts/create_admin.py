"""Bootstrap the first admin user. There is no public signup endpoint by design.

Usage:
    python -m scripts.create_admin --email admin@example.com --name "Admin"

You'll be prompted for a password interactively so it never appears in shell
history or process listings. For scripted/non-interactive use (e.g. a Docker
entrypoint), set ALTSMANAGER_ADMIN_PASSWORD in the environment instead.
"""

import argparse
import getpass
import os
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
    args = parser.parse_args()

    password = os.environ.get("ALTSMANAGER_ADMIN_PASSWORD")
    if not password:
        password = getpass.getpass("Password: ")
        if password != getpass.getpass("Confirm password: "):
            print("Passwords did not match.", file=sys.stderr)
            raise SystemExit(1)
    if len(password) < 8:
        print("Password must be at least 8 characters.", file=sys.stderr)
        raise SystemExit(1)

    with SessionLocal() as db:
        if get_user_by_email(db, args.email) is not None:
            print(f"User {args.email} already exists.", file=sys.stderr)
            raise SystemExit(1)

        user = User(
            email=args.email,
            full_name=args.name,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        print(f"Created admin user {user.email} ({user.id})")


if __name__ == "__main__":
    main()
