# ABOUTME: Authentication models extending core User model
# ABOUTME: Integrates fastapi-users with SQLModel User table

from ..models.user import User

# Use the extended User model as UserDB for fastapi-users
UserDB = User
