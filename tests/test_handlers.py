import json
from uuid import uuid4

# pytest_plugins = ('pytest_asyncio',)

# @pytest.mark.asyncio
#### pytest.ini

test_user_id = "98183338-6315-43ce-87ae-f8a2bf901094"
test_user_email = "somete2@domainte.kz"
test_update_user_id = "4fc6329e-29c5-4eb9-a01e-776f5320ff53"
test_update_user_email = "update@domainte.kz"


async def test_create_user(client, get_user_from_database):
    user_data = {
        "username": "art2000te",
        "name": "ArtemTE",
        "surname": "GorbunovTE",
        "email": "somete@domainte.kz"
    }
    resp = client.post("/user/create", content=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["username"] == user_data["username"]
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data["username"]
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]


async def test_get_all_users(client, create_user_in_database):
    user1_data = {
        "user_id": test_user_id,
        "username": "art2000te",
        "name": "ArtemTE",
        "surname": "GorbunovTE",
        "email": "somete@domainte.kz",
        "is_active": True
    }
    await create_user_in_database(**user1_data)
    user2_data = {
        "user_id": uuid4(),
        "username": "nik2000os",
        "name": "Nikke",
        "surname": "Volod",
        "email": test_user_email,
        "is_active": True
    }
    await create_user_in_database(**user2_data)
    
    resp_get = client.get(f"/user/get_all_users?limit=10&offset=0")
    users = resp_get.json()
    assert resp_get.status_code == 200
    assert len(users) == 2
    for user in users:
        resp = client.delete(f"/user/delete/?user_id_or_email={user['user_id']}")
        assert resp.status_code == 200

    resp_get = client.get(f"/user/get_all_users?limit=10&offset=0")
    users = resp_get.json()
    assert resp_get.status_code == 200
    assert len(users) == 0


async def test_get_by_id_or_email_user(client, create_user_in_database):
    user1_data = {
        "user_id": test_user_id,
        "username": "art2000te",
        "name": "ArtemTE",
        "surname": "GorbunovTE",
        "email": "somete@domainte.kz",
        "is_active": True
    }
    await create_user_in_database(**user1_data)
    user2_data = {
        "user_id": uuid4(),
        "username": "nik2000os",
        "name": "Nikke",
        "surname": "Volod",
        "email": test_user_email,
        "is_active": True
    }
    await create_user_in_database(**user2_data)
    
    resp_by_id = client.get(f"/user/get_by_id_or_email?user_id_or_email={test_user_id}")
    data_from_resp_by_id = resp_by_id.json()
    assert resp_by_id.status_code == 200
    assert data_from_resp_by_id['email'] != test_user_email
    resp_by_email = client.get(f"/user/get_by_id_or_email?user_id_or_email={test_user_email}")
    data_from_resp_by_email = resp_by_email.json()
    assert resp_by_email.status_code == 200
    assert data_from_resp_by_email['user_id'] != test_user_id

    resp = client.delete(f"/user/delete/?user_id_or_email={data_from_resp_by_id['user_id']}")
    assert resp.status_code == 200
    resp = client.delete(f"/user/delete/?user_id_or_email={data_from_resp_by_email['user_id']}")
    assert resp.status_code == 200

    resp_by_id_deleted = client.get(f"/user/get_by_id_or_email?user_id_or_email={test_user_id}")
    assert resp_by_id_deleted.status_code == 404


async def test_update_user(client, create_user_in_database, get_user_from_database):
    user_data = {"user_id": test_update_user_id,
                 "username": "art2000te",
                 "name": "ArtemTE",
                 "surname": "GorbunovTE",
                 "email": test_update_user_email,
                 "is_active": True}
    await create_user_in_database(**user_data)

    users_from_db = await get_user_from_database(user_data["user_id"])
    assert len(users_from_db) == 1
    upd_data = {"name": "newname",
                "surname": "newsurname"}
    
    resp = client.put(f"/user/update?user_id={user_data['user_id']}", content=json.dumps(upd_data))
    assert resp.status_code == 200
    users_from_db = await get_user_from_database(user_data["user_id"])
    assert len(users_from_db) == 1
    updated_user_from_db = dict(users_from_db[0])
    assert updated_user_from_db["name"] == upd_data["name"]
    assert updated_user_from_db["surname"] == upd_data["surname"]


async def test_activate_deactivate_user(client, create_user_in_database, get_user_from_database):
    user_data = {"user_id": uuid4(),
                 "username": "deactivatetest",
                 "name": "deactivate",
                 "surname": "test",
                 "email": "de@activate.net",
                 "is_active": True}
    await create_user_in_database(**user_data)
    resp = client.patch(f"user/deactivate?user_id_or_email={user_data['user_id']}")
    assert resp.status_code == 200
    users_from_db = await get_user_from_database(user_data["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["is_active"] == False

    resp = client.patch(f"user/activate?user_id_or_email={user_from_db['user_id']}")
    assert resp.status_code == 200
    users_from_db = await get_user_from_database(user_data["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["is_active"] == True


async def test_delete_user(client, create_user_in_database, get_user_from_database):
    user_data = {"user_id": uuid4(),
                 "username": "art2000te",
                 "name": "ArtemTE",
                 "surname": "GorbunovTE",
                 "email": "somete@domainte.kz",
                 "is_active": True}
    await create_user_in_database(**user_data)
    resp = client.delete(f"/user/delete/?user_id_or_email={user_data['user_id']}")
    data_from_resp = resp.json()
    assert resp.status_code == 200
    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 0
