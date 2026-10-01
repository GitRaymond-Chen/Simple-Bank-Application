from pymongo.database import Database

from app.database import next_id
from app.models import User, utcnow


class UserRepository:
    """
    Handles all database operations for users.
    The repository pattern keeps MongoDB queries in one place,
    separate from business logic.
    """

    def __init__(self, db: Database):
        self.users = db.users
        self.db = db

    def create(self, name: str, email: str) -> User:
        """Insert a new user document and return it."""
        doc = {"_id": next_id(self.db, "users"), "name": name, "email": email,
               "created_at": utcnow()}
        self.users.insert_one(doc)  # unique index on email raises DuplicateKeyError on a race
        return User.from_doc(doc)

    def get_by_id(self, user_id: int) -> User | None:
        """Look up a user by id. Returns None if not found."""
        doc = self.users.find_one({"_id": user_id})
        return User.from_doc(doc) if doc else None

    def get_by_email(self, email: str) -> User | None:
        """Look up a user by their unique email address."""
        doc = self.users.find_one({"email": email})
        return User.from_doc(doc) if doc else None
