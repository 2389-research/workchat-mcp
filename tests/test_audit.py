# ABOUTME: Audit log endpoint and service tests
# ABOUTME: Test audit trail creation, admin access control, and JSON diff tracking

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlmodel import select

from workchat.models import AuditLog, Channel, Org, User, UserRole


class TestAuditService:
    """Test audit service functionality."""

    def test_track_message_update(
        self,
        client: TestClient,
        test_user_headers: dict,
        test_org: Org,
        test_user: User,
        session: Session,
    ):
        """Test that editing a message creates exactly one audit row with correct payload."""
        # Create a channel
        channel = Channel(
            org_id=test_org.id,
            name="general",
            description="General channel",
        )
        session.add(channel)
        session.commit()

        # Create a message
        message_data = {
            "body": "Original message content",
            "thread_id": None,
        }

        response = client.post(
            f"/api/messages/?channel_id={channel.id}",
            json=message_data,
            headers=test_user_headers,
        )
        assert response.status_code == 201
        message_id = response.json()["id"]

        # Check no audit logs exist yet
        audit_count_before = len(session.exec(select(AuditLog)).all())
        assert audit_count_before == 0

        # Edit the message
        edit_data = {
            "body": "Updated message content",
            "version": 1,
        }

        response = client.patch(
            f"/api/messages/{message_id}",
            json=edit_data,
            headers=test_user_headers,
        )
        assert response.status_code == 200

        # Check exactly one audit log was created
        audit_logs = session.exec(select(AuditLog)).all()
        assert len(audit_logs) == 1

        audit_log = audit_logs[0]
        assert audit_log.entity_type == "message"
        assert audit_log.entity_id == UUID(message_id)
        assert audit_log.user_id == test_user.id
        assert audit_log.action == "update"

        # Verify JSON diff content
        assert audit_log.old_values is not None
        assert audit_log.new_values is not None
        assert audit_log.old_values["body"] == "Original message content"
        assert audit_log.new_values["body"] == "Updated message content"
        assert audit_log.old_values["version"] == 1
        assert audit_log.new_values["version"] == 2

        # Verify metadata
        assert audit_log.endpoint == "PATCH /api/messages/" + message_id
        assert audit_log.ip_address is not None


class TestAuditAPI:
    """Test audit API endpoints."""

    def test_audit_requires_admin(
        self,
        client: TestClient,
        test_user_headers: dict,
    ):
        """Test that audit endpoints require admin access."""
        response = client.get("/api/audit/", headers=test_user_headers)
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_list_audit_logs_admin_access(
        self,
        client: TestClient,
        test_org: Org,
        session: Session,
    ):
        """Test that admin users can access audit logs."""
        # Create an admin user
        admin_user = User(
            org_id=test_org.id,
            display_name="Admin User",
            email="admin@example.com",
            role=UserRole.ADMIN,
            hashed_password="$2b$12$test_hashed_password",
            is_active=True,
            is_verified=True,
        )
        session.add(admin_user)
        session.commit()

        # Override auth dependency for admin user
        from workchat.app import app
        from workchat.auth import current_active_user

        def override_current_active_user():
            return admin_user

        app.dependency_overrides[current_active_user] = override_current_active_user

        try:
            response = client.get("/api/audit/")
            assert response.status_code == 200
            data = response.json()
            assert "audit_logs" in data
            assert "total_count" in data
            assert "limit" in data
            assert "offset" in data
        finally:
            # Clean up override
            if current_active_user in app.dependency_overrides:
                del app.dependency_overrides[current_active_user]

    def test_audit_log_filtering(
        self,
        client: TestClient,
        test_org: Org,
        test_user: User,
        session: Session,
    ):
        """Test audit log filtering by entity type and action."""
        # Create admin user
        admin_user = User(
            org_id=test_org.id,
            display_name="Admin User",
            email="admin@example.com",
            role=UserRole.ADMIN,
            hashed_password="$2b$12$test_hashed_password",
            is_active=True,
            is_verified=True,
        )
        session.add(admin_user)

        # Create test audit logs
        audit1 = AuditLog(
            entity_type="message",
            entity_id=test_user.id,  # Using user id as placeholder
            user_id=test_user.id,
            action="update",
            old_values={"body": "old"},
            new_values={"body": "new"},
        )
        audit2 = AuditLog(
            entity_type="channel",
            entity_id=test_user.id,  # Using user id as placeholder
            user_id=test_user.id,
            action="create",
            new_values={"name": "test-channel"},
        )
        session.add(audit1)
        session.add(audit2)
        session.commit()

        # Override auth for admin
        from workchat.app import app
        from workchat.auth import current_active_user

        def override_current_active_user():
            return admin_user

        app.dependency_overrides[current_active_user] = override_current_active_user

        try:
            # Test entity type filtering
            response = client.get("/api/audit/?entity_type=message")
            assert response.status_code == 200
            data = response.json()
            assert len(data["audit_logs"]) == 1
            assert data["audit_logs"][0]["entity_type"] == "message"

            # Test action filtering
            response = client.get("/api/audit/?action=create")
            assert response.status_code == 200
            data = response.json()
            assert len(data["audit_logs"]) == 1
            assert data["audit_logs"][0]["action"] == "create"

            # Test pagination
            response = client.get("/api/audit/?limit=1&offset=0")
            assert response.status_code == 200
            data = response.json()
            assert len(data["audit_logs"]) == 1
            assert data["total_count"] == 2

        finally:
            # Clean up override
            if current_active_user in app.dependency_overrides:
                del app.dependency_overrides[current_active_user]

    def test_entity_audit_history(
        self,
        client: TestClient,
        test_org: Org,
        test_user: User,
        session: Session,
    ):
        """Test getting complete audit history for an entity."""
        # Create admin user
        admin_user = User(
            org_id=test_org.id,
            display_name="Admin User",
            email="admin@example.com",
            role=UserRole.ADMIN,
            hashed_password="$2b$12$test_hashed_password",
            is_active=True,
            is_verified=True,
        )
        session.add(admin_user)

        entity_id = test_user.id  # Using user id as placeholder

        # Create multiple audit entries for same entity
        audit1 = AuditLog(
            entity_type="message",
            entity_id=entity_id,
            user_id=test_user.id,
            action="create",
            new_values={"body": "original"},
        )
        audit2 = AuditLog(
            entity_type="message",
            entity_id=entity_id,
            user_id=test_user.id,
            action="update",
            old_values={"body": "original"},
            new_values={"body": "updated"},
        )
        session.add(audit1)
        session.add(audit2)
        session.commit()

        # Override auth for admin
        from workchat.app import app
        from workchat.auth import current_active_user

        def override_current_active_user():
            return admin_user

        app.dependency_overrides[current_active_user] = override_current_active_user

        try:
            response = client.get(f"/api/audit/entity/message/{entity_id}")
            assert response.status_code == 200
            data = response.json()

            assert len(data) == 2
            # Should be ordered chronologically (oldest first)
            assert data[0]["action"] == "create"
            assert data[1]["action"] == "update"

        finally:
            # Clean up override
            if current_active_user in app.dependency_overrides:
                del app.dependency_overrides[current_active_user]
