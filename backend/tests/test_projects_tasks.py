from tests.conftest import auth_headers, user_id


def setup_project(client):
    lead = auth_headers(client, "lead@example.com", "lead123")
    dev = auth_headers(client, "dev@example.com", "dev123")
    outsider = auth_headers(client, "outsider@example.com", "out123")
    project = client.post("/api/projects", json={"name": "Website Launch", "description": "x"}, headers=lead).json()
    dev_id = user_id(client, dev, "dev@example.com")
    client.post(f"/api/projects/{project['id']}/members", json={"user_id": dev_id}, headers=lead)
    return lead, dev, outsider, project


def test_create_project_owner_is_member(client):
    lead, dev, outsider, project = setup_project(client)
    members = client.get(f"/api/projects/{project['id']}", headers=lead).json()["members"]
    assert any(m["role"] == "owner" for m in members)


def test_non_member_cannot_read_project(client):
    lead, dev, outsider, project = setup_project(client)
    # Non-members get a 404 (existence is not leaked).
    assert client.get(f"/api/projects/{project['id']}", headers=outsider).status_code == 404


def test_task_assignment_must_be_member(client):
    lead, dev, outsider, project = setup_project(client)
    outsider_id = user_id(client, outsider, "outsider@example.com")
    resp = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Task", "assignee_id": outsider_id},
        headers=lead,
    )
    assert resp.status_code == 422


def test_task_workflow_transitions(client):
    lead, dev, outsider, project = setup_project(client)
    task = client.post(f"/api/projects/{project['id']}/tasks", json={"title": "Build it"}, headers=lead).json()

    ok = client.patch(f"/api/tasks/{task['id']}", json={"status": "In Progress"}, headers=dev)
    assert ok.status_code == 200

    # To Do -> Done directly is not allowed.
    task2 = client.post(f"/api/projects/{project['id']}/tasks", json={"title": "Another"}, headers=lead).json()
    bad = client.patch(f"/api/tasks/{task2['id']}", json={"status": "Done"}, headers=lead)
    assert bad.status_code == 422


def test_outsider_cannot_see_tasks(client):
    lead, dev, outsider, project = setup_project(client)
    client.post(f"/api/projects/{project['id']}/tasks", json={"title": "Secret"}, headers=lead)
    listing = client.get("/api/tasks", headers=outsider).json()
    assert listing["total"] == 0


def test_comment_and_summary_and_overdue(client):
    lead, dev, outsider, project = setup_project(client)
    task = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Overdue task", "due_date": "2000-01-01"},
        headers=lead,
    ).json()

    c = client.post(f"/api/tasks/{task['id']}/comments", json={"body": "On it"}, headers=dev)
    assert c.status_code == 201

    detail = client.get(f"/api/tasks/{task['id']}", headers=dev).json()
    assert len(detail["comments"]) == 1

    summary = client.get(f"/api/projects/{project['id']}/summary", headers=lead).json()
    assert summary["total"] == 1
    assert summary["overdue"] == 1

    dash = client.get("/api/dashboard/summary", headers=lead).json()
    assert dash["overdue"] >= 1
