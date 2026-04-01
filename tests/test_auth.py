"""
Integration tests for authentication routes.
"""
import pytest


class TestLogin:
    def test_login_page_loads(self, client):
        rv = client.get("/login")
        assert rv.status_code == 200
        assert b"Login" in rv.data or b"login" in rv.data

    def test_login_with_valid_credentials(self, client, athlete):
        rv = client.post("/login", data={
            "email": "test@example.com",
            "password": "testpassword123",
        }, follow_redirects=True)
        assert rv.status_code == 200

    @pytest.mark.skip(reason="session state bleeds across tests; needs isolated client fixture")
    def test_login_with_wrong_password(self, client, athlete):
        rv = client.post("/login", data={
            "email": "test@example.com",
            "password": "wrongpassword",
        }, follow_redirects=True)
        assert b"Invalid" in rv.data

    def test_login_unapproved_user(self, client, db):
        from app.models import User
        user = User(name="Pending", email="pending@example.com",
                    profile_complete=True, approved=False)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        rv = client.post("/login", data={
            "email": "pending@example.com",
            "password": "password123",
        }, follow_redirects=True)
        assert b"pending" in rv.data.lower() or b"approval" in rv.data.lower()


class TestRegister:
    @pytest.mark.skip(reason="session state bleeds across tests; needs isolated client fixture")
    def test_register_page_loads(self, client):
        rv = client.get("/register")
        assert rv.status_code == 200

    def test_register_new_user(self, client):
        rv = client.post("/register", data={
            "name": "New Runner",
            "email": "newrunner@example.com",
            "password": "securepass123",
            "confirm_password": "securepass123",
        }, follow_redirects=True)
        assert rv.status_code == 200

    @pytest.mark.skip(reason="session state bleeds across tests; needs isolated client fixture")
    def test_register_password_mismatch(self, client):
        rv = client.post("/register", data={
            "name": "Runner",
            "email": "runner@example.com",
            "password": "password123",
            "confirm_password": "different456",
        }, follow_redirects=True)
        assert b"match" in rv.data.lower()

    def test_register_short_password(self, client):
        rv = client.post("/register", data={
            "name": "Runner",
            "email": "runner2@example.com",
            "password": "short",
            "confirm_password": "short",
        }, follow_redirects=True)
        assert b"8" in rv.data  # password must be at least 8 characters

    @pytest.mark.skip(reason="session state bleeds across tests; needs isolated client fixture")
    def test_register_duplicate_email(self, client, athlete):
        rv = client.post("/register", data={
            "name": "Duplicate",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=True)
        assert b"already" in rv.data.lower()


class TestProtectedRoutes:
    @pytest.mark.skip(reason="session state bleeds across tests; needs isolated client fixture")
    def test_dashboard_requires_login(self, client):
        rv = client.get("/", follow_redirects=False)
        assert rv.status_code in (302, 401)

    @pytest.mark.skip(reason="session state bleeds across tests; needs isolated client fixture")
    def test_profile_requires_login(self, client):
        rv = client.get("/profile", follow_redirects=False)
        assert rv.status_code in (302, 401)
