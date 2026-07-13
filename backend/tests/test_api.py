from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'operational'


def test_dashboard_seeded():
    data = client.get('/api/dashboard').json()
    assert data['profile']['name'] == 'Mani'
    assert len(data['missions']) >= 7
    assert len(data['competencies']) >= 8


def test_complete_mission_updates_progress():
    before = client.get('/api/dashboard').json()['profile']['xp']
    response = client.post('/api/missions/1/complete', json={'score': 88, 'reflection': 'Validated inventory flow.'})
    assert response.status_code == 200
    assert response.json()['mission']['status'] == 'verified'
    after = client.get('/api/dashboard').json()['profile']['xp']
    assert after >= before


def test_simulator_calculates_inventory_controls():
    response = client.post('/api/simulate', json={
        'daily_demand': 42, 'lead_time': 7, 'demand_std': 8,
        'service_z': 1.65, 'review_period': 1
    })
    data = response.json()
    assert data['safety_stock'] > 0
    assert data['reorder_point'] > data['safety_stock']


def test_all_screen_collections_exist():
    data = client.get('/api/dashboard').json()
    for key in ['missions', 'competencies', 'rewards', 'portfolio', 'manager_cases', 'learning_map']:
        assert key in data
        assert data[key]
