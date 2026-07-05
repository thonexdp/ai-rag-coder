def test_register_and_login(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "learner@example.com",
            "full_name": "Learner One",
            "password": "StrongPass123",
            "role": "student",
        },
    )
    assert register_response.status_code == 200
    assert register_response.json()["email"] == "learner@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "learner@example.com", "password": "StrongPass123"},
    )
    assert login_response.status_code == 200
    body = login_response.json()
    assert body["access_token"]
    assert body["user"]["role"] == "student"


def test_invalid_login(client):
    response = client.post("/api/v1/auth/login", json={"email": "missing@example.com", "password": "badpass"})
    assert response.status_code == 401
