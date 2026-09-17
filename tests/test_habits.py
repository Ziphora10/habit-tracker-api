def test_create_and_list_habit(client, auth_headers):
    response = client.post(
        "/habits",
        json={"name": "Read", "description": "Read 10 pages"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    habit = response.json()
    assert habit["name"] == "Read"

    response = client.get("/habits", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_update_delete_habit(client, auth_headers):
    create = client.post(
        "/habits", json={"name": "Exercise"}, headers=auth_headers
    )
    habit_id = create.json()["id"]

    get_resp = client.get(f"/habits/{habit_id}", headers=auth_headers)
    assert get_resp.status_code == 200

    update_resp = client.put(
        f"/habits/{habit_id}", json={"name": "Exercise Daily"}, headers=auth_headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Exercise Daily"

    delete_resp = client.delete(f"/habits/{habit_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    missing_resp = client.get(f"/habits/{habit_id}", headers=auth_headers)
    assert missing_resp.status_code == 404


def test_cannot_access_another_users_habit(client, auth_headers):
    create = client.post(
        "/habits", json={"name": "Meditate"}, headers=auth_headers
    )
    habit_id = create.json()["id"]

    client.post(
        "/auth/signup", json={"email": "other@example.com", "password": "secret123"}
    )
    login = client.post(
        "/auth/login",
        data={"username": "other@example.com", "password": "secret123"},
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get(f"/habits/{habit_id}", headers=other_headers)
    assert response.status_code == 404


def test_mark_done_today_and_duplicate_rejected(client, auth_headers):
    create = client.post(
        "/habits", json={"name": "Stretch"}, headers=auth_headers
    )
    habit_id = create.json()["id"]

    first = client.post(f"/habits/{habit_id}/complete", headers=auth_headers)
    assert first.status_code == 201

    second = client.post(f"/habits/{habit_id}/complete", headers=auth_headers)
    assert second.status_code == 400


def test_streak_with_no_completions(client, auth_headers):
    create = client.post(
        "/habits", json={"name": "Journal"}, headers=auth_headers
    )
    habit_id = create.json()["id"]

    response = client.get(f"/habits/{habit_id}/streak", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["current_streak"] == 0
    assert body["longest_streak"] == 0
    assert body["total_completions"] == 0


def test_streak_after_marking_today(client, auth_headers):
    create = client.post(
        "/habits", json={"name": "Water plants"}, headers=auth_headers
    )
    habit_id = create.json()["id"]

    client.post(f"/habits/{habit_id}/complete", headers=auth_headers)

    response = client.get(f"/habits/{habit_id}/streak", headers=auth_headers)
    body = response.json()
    assert body["current_streak"] == 1
    assert body["longest_streak"] == 1
    assert body["total_completions"] == 1
