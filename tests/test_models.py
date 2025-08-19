# ABOUTME: Domain model tests
# ABOUTME: Tests table creation and basic CRUD operations for Org and User models

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from workchat.models import Org, User, UserRole


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_org_model_creation(session: Session):
    """Test creating an Org model."""
    org = Org(name="Test Organization")
    session.add(org)
    session.commit()
    session.refresh(org)

    assert org.id is not None
    assert org.name == "Test Organization"
    assert org.created_at is not None


def test_user_model_creation(session: Session):
    """Test creating a User model with org relationship."""
    # Create organization first
    org = Org(name="Test Org")
    session.add(org)
    session.commit()
    session.refresh(org)

    # Create user
    user = User(
        org_id=org.id,
        display_name="John Doe",
        email="john@example.com",
        role=UserRole.ADMIN,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.id is not None
    assert user.org_id == org.id
    assert user.display_name == "John Doe"
    assert user.email == "john@example.com"
    assert user.role == UserRole.ADMIN
    assert user.created_at is not None


def test_org_user_relationship(session: Session):
    """Test the relationship between Org and User."""
    # Create organization
    org = Org(name="Test Org")
    session.add(org)
    session.commit()
    session.refresh(org)

    # Create users
    user1 = User(
        org_id=org.id,
        display_name="User One",
        email="user1@example.com",
        role=UserRole.ADMIN,
    )
    user2 = User(
        org_id=org.id,
        display_name="User Two",
        email="user2@example.com",
        role=UserRole.MEMBER,
    )

    session.add_all([user1, user2])
    session.commit()

    # Test relationship - fetch org with users
    org_with_users = session.get(Org, org.id)
    assert org_with_users is not None
    assert len(org_with_users.users) == 2

    # Test reverse relationship
    user_with_org = session.get(User, user1.id)
    assert user_with_org is not None
    assert user_with_org.org.name == "Test Org"


def test_org_name_uniqueness(session: Session):
    """Test that org names must be unique."""
    org1 = Org(name="Unique Org")
    org2 = Org(name="Unique Org")

    session.add(org1)
    session.commit()

    session.add(org2)
    with pytest.raises(Exception):  # SQLite will raise IntegrityError
        session.commit()


def test_user_email_uniqueness(session: Session):
    """Test that user emails must be unique."""
    org = Org(name="Test Org")
    session.add(org)
    session.commit()

    user1 = User(org_id=org.id, display_name="User 1", email="same@example.com")
    user2 = User(org_id=org.id, display_name="User 2", email="same@example.com")

    session.add(user1)
    session.commit()

    session.add(user2)
    with pytest.raises(Exception):  # SQLite will raise IntegrityError
        session.commit()


def test_user_default_role(session: Session):
    """Test that users default to MEMBER role."""
    org = Org(name="Test Org")
    session.add(org)
    session.commit()

    user = User(org_id=org.id, display_name="Default User", email="default@example.com")
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.role == UserRole.MEMBER


def test_crud_operations(session: Session):
    """Test basic CRUD operations on models."""
    # Create
    org = Org(name="CRUD Test Org")
    session.add(org)
    session.commit()
    session.refresh(org)

    user = User(
        org_id=org.id,
        display_name="CRUD User",
        email="crud@example.com",
        role=UserRole.ADMIN,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Read
    fetched_org = session.get(Org, org.id)
    assert fetched_org is not None
    assert fetched_org.name == "CRUD Test Org"

    fetched_user = session.get(User, user.id)
    assert fetched_user is not None
    assert fetched_user.email == "crud@example.com"

    # Update
    fetched_user.display_name = "Updated User"
    session.commit()
    session.refresh(fetched_user)
    assert fetched_user.display_name == "Updated User"

    # Delete
    session.delete(fetched_user)
    session.commit()

    deleted_user = session.get(User, user.id)
    assert deleted_user is None

    # Org should still exist
    remaining_org = session.get(Org, org.id)
    assert remaining_org is not None


def test_query_operations(session: Session):
    """Test querying models with SQLModel select."""
    # Setup test data
    org1 = Org(name="First Org")
    org2 = Org(name="Second Org")
    session.add_all([org1, org2])
    session.commit()

    user1 = User(
        org_id=org1.id,
        display_name="Admin User",
        email="admin@first.com",
        role=UserRole.ADMIN,
    )
    user2 = User(
        org_id=org1.id,
        display_name="Member User",
        email="member@first.com",
        role=UserRole.MEMBER,
    )
    user3 = User(
        org_id=org2.id,
        display_name="Another Admin",
        email="admin@second.com",
        role=UserRole.ADMIN,
    )
    session.add_all([user1, user2, user3])
    session.commit()

    # Test querying all orgs
    statement = select(Org)
    orgs = session.exec(statement).all()
    assert len(orgs) == 2

    # Test querying users by role
    statement = select(User).where(User.role == UserRole.ADMIN)
    admins = session.exec(statement).all()
    assert len(admins) == 2

    # Test querying users by org
    statement = select(User).where(User.org_id == org1.id)
    org1_users = session.exec(statement).all()
    assert len(org1_users) == 2


def test_model_serialization():
    """Test model serialization and deserialization."""
    from uuid import uuid4

    # Test creating models with all fields
    org_id = uuid4()
    org = Org(id=org_id, name="Test Org")
    assert org.id == org_id
    assert org.name == "Test Org"

    user_id = uuid4()
    user = User(
        id=user_id,
        org_id=org_id,
        display_name="Test User",
        email="test@example.com",
        role=UserRole.ADMIN,
    )
    assert user.id == user_id
    assert user.org_id == org_id
    assert user.display_name == "Test User"
    assert user.email == "test@example.com"
    assert user.role == UserRole.ADMIN
