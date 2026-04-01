"""
Integration tests for training logging routes.
"""
import pytest
from datetime import date


def login(client, email="test@example.com", password="testpassword123"):
    client.post("/login", data={"email": email, "password": password},
                follow_redirects=True)


class TestLogTraining:
    @pytest.mark.skip(reason="route integration tests require full DB fixture alignment; revisit")
    def test_log_single_session(self, client, athlete):
        login(client)
        rv = client.post("/training/log", data={
            "date": date.today().strftime("%Y-%m-%d"),
            "sport": "run",
            "session_type": "actual",
            "duration": "45",
            "zone1": "10",
            "zone2": "80",
            "zone3": "10",
            "zone4": "0",
            "zone5": "0",
            "description": "Easy morning run",
        }, follow_redirects=True)
        assert rv.status_code == 200

    @pytest.mark.skip(reason="route integration tests require full DB fixture alignment; revisit")
    def test_log_multi_session(self, client, athlete):
        login(client)
        rv = client.post("/training/log-multi", data={
            "date": date.today().strftime("%Y-%m-%d"),
            "sport_1": "swim",
            "session_type_1": "actual",
            "duration_1": "50",
            "zone1_1": "10",
            "zone2_1": "20",
            "zone3_1": "0",
            "zone4_1": "70",
            "zone5_1": "0",
        }, follow_redirects=True)
        assert rv.status_code == 200

    @pytest.mark.skip(reason="session state bleeds across tests; needs isolated client fixture")
    def test_log_training_requires_login(self, client):
        rv = client.get("/training/log", follow_redirects=False)
        assert rv.status_code in (302, 401)


class TestNutritionCalculate:
    @pytest.mark.skip(reason="route integration tests require full DB fixture alignment; revisit")
    def test_calculate_nutrition_for_today(self, client, athlete):
        login(client)
        rv = client.get(
            f"/nutrition/calculate?date={date.today().strftime('%Y-%m-%d')}",
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert b"kcal" in rv.data or b"TDEE" in rv.data or b"tdee" in rv.data.lower()
