import os
import pytest

TEST_DB = "db/test_members.db"


@pytest.fixture
def client():
    import gc

    # Ensure db directory exists
    os.makedirs("db", exist_ok=True)

    # Remove old test DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Set DB path BEFORE importing app
    from app.models.db_init import set_db_path, init_db
    set_db_path(TEST_DB)

    # Import Flask app AFTER DB is configured
    from app.app import app

    app.config["TESTING"] = True

    # Initialize fresh database
    init_db(TEST_DB)

    with app.test_client() as client:
        # Login with static credentials
        client.post(
            "/", data={"username": "admin", "password": "admin123"},
            follow_redirects=True
        )
        yield client

    # Cleanup
    gc.collect()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Restore original DB
    set_db_path("db/members.db")




#######################################################
# import os
# import pytest
# from pathlib import Path

# TEST_DB = "db/test_members.db"

# @pytest.fixture
# def client():
#     import gc

#     # Ensure db directory exists
#     os.makedirs("db", exist_ok=True)

#     # Remove old test DB
#     if os.path.exists(TEST_DB):
#         os.remove(TEST_DB)

#     # 🔑 Set DB path BEFORE importing app
#     from app.models.db_init import set_db_path, init_db
#     set_db_path(TEST_DB)

#     # Import app ONLY after DB is configured
#     from app.app import app

#     app.config["TESTING"] = True

#     # Initialize fresh database
#     init_db(TEST_DB)

#     with app.test_client() as client:
#         # Login
#         client.post(
#             "/", data={"username": "admin", "password": "admin123"},
#             follow_redirects=True
#         )
#         yield client

#     # Cleanup
#     gc.collect()
#     if os.path.exists(TEST_DB):
#         os.remove(TEST_DB)

#     # Restore original DB
#     set_db_path("db/members.db")
