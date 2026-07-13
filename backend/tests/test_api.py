import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

TEST_DB = Path(tempfile.gettempdir()) / 'inventory_learning_pytest.db'
TEST_DB.unlink(missing_ok=True)
os.environ['INVENTORY_DB_PATH'] = str(TEST_DB)

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'operational'
    assert response.json()['database'] == str(TEST_DB)


def test_dashboard_seeded():
    data = client.get('/api/dashboard').json()
    assert data['profile']['name'] == 'Mani'
    assert len(data['missions']) >= 7
    assert len(data['competencies']) >= 8


def test_complete_mission_updates_progress():
    before = client.get('/api/dashboard').json()['profile']['xp']
    response = client.post('/api/missions/1/complete', json={
        'score': 88,
        'reflection': 'Validated inventory flow and documented each control point.',
    })
    assert response.status_code == 200
    assert response.json()['mission']['status'] == 'verified'
    after = client.get('/api/dashboard').json()['profile']['xp']
    assert after >= before


def test_simulator_calculates_inventory_controls():
    response = client.post('/api/simulate', json={
        'daily_demand': 42, 'lead_time': 7, 'demand_std': 8,
        'service_z': 1.65, 'review_period': 1,
    })
    data = response.json()
    assert data['safety_stock'] > 0
    assert data['reorder_point'] > data['safety_stock']


def test_all_screen_collections_exist():
    data = client.get('/api/dashboard').json()
    for key in ['missions', 'competencies', 'rewards', 'portfolio', 'manager_cases', 'learning_map']:
        assert key in data
        assert data[key]


def test_reward_unlocks_and_can_be_claimed_after_verified_work():
    # Reward 2 requires five missions; only mission 1 is verified at this point.
    locked = client.post('/api/rewards/2/claim')
    assert locked.status_code == 409

    for mission_id in range(2, 6):
        client.post(f'/api/missions/{mission_id}/complete', json={
            'score': 88,
            'reflection': 'Completed the required analysis and documented control points.',
        })
    reward = next(r for r in client.get('/api/dashboard').json()['rewards'] if r['id'] == 2)
    assert reward['unlocked'] is True
    assert reward['claimed'] is False

    claimed = client.post('/api/rewards/2/claim')
    assert claimed.status_code == 200
    assert claimed.json()['reward']['claimed'] is True

    reward = next(r for r in client.get('/api/dashboard').json()['rewards'] if r['id'] == 2)
    assert reward['claimed'] is True
