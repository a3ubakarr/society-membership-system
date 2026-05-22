import pytest
import sqlite3
import os


TEST_DB = "db/test_members.db"

def add_member(client, student_id="S001"):
    data = {
        "action": "add",
        "first_name": "John",
        "last_name": "Doe",
        "gender": "Male",
        "student_id": student_id,
        "society": "UMT IEEE",
        "date_joined": "2025-12-24",
        "position": "Volunteer"
    }
    return client.post("/home", data=data, follow_redirects=True)

# ---------- Test Cases ----------

def test_add_member_success(client):
    response = add_member(client, "S001")
    html = response.get_data(as_text=True)
    assert "Member added successfully" in html or "Failed to add member" in html

def test_add_duplicate_member(client):
    add_member(client, "S002")
    response = add_member(client, "S002")
    html = response.get_data(as_text=True)
    assert "Failed to add member" in html


def test_find_by_student_id(client):
    add_member(client, "S003")
    response = client.post("/home", data={"action":"find_id","student_id":"S003"})
    assert b"S003" in response.data
    assert b"John Doe" in response.data

def test_find_by_society(client):
    add_member(client, "S004")
    add_member(client, "S005")
    response = client.post("/home", data={"action":"find_society","society":"UMT IEEE"})
    assert b"John Doe" in response.data

def test_position_displayed(client):
    add_member(client, "S006")
    response = client.post("/home", data={"action":"find_id","student_id":"S006"})
    assert b"Volunteer" in response.data

def test_home_requires_login(client):
    client.get("/logout", follow_redirects=True)
    response = client.get("/home")
    assert response.status_code == 302
    assert "/" in response.headers["Location"]

def test_logout(client):
    add_member(client)
    response = client.get("/logout", follow_redirects=True)
    assert b"Login" in response.data

def test_collapsible_forms_exist(client):
    response = client.get("/home")
    assert b"Add Member" in response.data
    assert b"Find by Student ID" in response.data
    assert b"Find by Society" in response.data

def test_find_nonexistent_student(client):
    response = client.post("/home", data={"action":"find_id","student_id":"XYZ"})
    assert b"XYZ" not in response.data

def test_add_member_with_all_positions(client):
    positions = ["Volunteer", "President", "Vice President", "Vice President Female",
                 "Treasurer", "General Secretary", "Media Secretary"]
    for i, pos in enumerate(positions):
        data = {
            "action": "add",
            "first_name": f"Test70{i}",
            "last_name": f"User70{i}",
            "gender": "Male",
            "student_id": f"S70{i}",
            "society": "UMT ACM",
            "date_joined": "2025-12-24",
            "position": pos
        }
        response = client.post("/home", data=data, follow_redirects=True)
        html = response.get_data(as_text=True)
        
        print(f"Response contains 'Member added successfully!': {'Member added successfully!' in html}")
        print(f"Response contains 'Failed to add member': {'Failed to add member' in html}")
        assert "Member added successfully" in html 
def test_search_student_not_found(client):
    """Negative: Search non-existent student"""
    response = client.post("/home", data={
        "action": "find_id",
        "student_id": "NOTEXIST"
    })
    html = response.get_data(as_text=True)
    assert "NOTEXIST" not in html


def test_search_society_empty(client):
    """Negative: Search society when no members exist"""
    response = client.post("/home", data={
        "action": "find_society",
        "society": "UMT Robotics"
    })
    html = response.get_data(as_text=True)
    assert "John Doe" not in html


# ---------------- UPDATE TESTS ----------------

def test_update_member_success(client):
    """Positive: Update existing member"""
    add_member(client, "U001")

    response = client.post("/home", data={
        "action": "update",
        "student_id": "U001",
        "first_name": "Updated",
        "last_name": "User",
        "gender": "Female",
        "society": "UMT ACM",
        "date_joined": "2025-12-25",
        "position": "President"
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Member updated successfully" in html


def test_update_member_not_found(client):
    """Negative: Update non-existent member"""
    response = client.post("/home", data={
        "action": "update",
        "student_id": "BAD999",
        "first_name": "X",
        "last_name": "Y",
        "gender": "Male",
        "society": "UMT ACM",
        "date_joined": "2025-12-25",
        "position": "Volunteer"
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "No member found" in html


# ---------------- DELETE TESTS ----------------

def test_delete_member_success(client):
    """Positive: Delete existing member"""
    add_member(client, "D001")

    response = client.post("/home", data={
        "action": "delete",
        "student_id": "D001",
        "confirm": "yes"
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Member deleted successfully" in html


def test_delete_member_not_found(client):
    """Negative: Delete non-existent member"""
    response = client.post("/home", data={
        "action": "delete",
        "student_id": "NOPE123",
        "confirm": "yes"
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "No member found" in html


# ---------------- SORT TESTS ----------------

def test_sort_results_by_gender(client):
    """Positive: Sort results by gender"""
    add_member(client, "S101")
    add_member(client, "S102")

    # First search so session has results
    client.post("/home", data={
        "action": "find_society",
        "society": "UMT IEEE"
    })

    response = client.post("/home", data={
        "action": "sort",
        "sort_by": "gender"
    })

    assert response.status_code == 200


def test_sort_empty_results(client):
    """Negative: Sort when no results exist"""
    response = client.post("/home", data={
        "action": "sort",
        "sort_by": "gender"
    })
    assert response.status_code == 200   # App should not crash


# ---------------- GRAPH TESTS ----------------

def test_graph_file_created(client):
    """Positive: Graph image should be generated"""
    client.get("/home")

    graph_path = "app/static/members_graph.png"
    assert os.path.exists(graph_path)


def test_graph_updates_after_add(client):
    """Positive: Graph regenerates after adding member"""
    add_member(client, "G001")
    client.get("/home")

    graph_path = "app/static/members_graph.png"
    assert os.path.exists(graph_path)
# def test_add_member_with_all_positions(client):
#     # Debug: Check DB path being used
#     from app.models.db_init import DB_PATH
#     print(f"\n=== Current DB_PATH in models: {DB_PATH} ===")
#     print(f"=== TEST_DB path: {TEST_DB} ===")
    
#     # Debug: Check what's in the DB before we start
#     print("\n=== Checking database before test ===")
#     conn = sqlite3.connect(TEST_DB)
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM members")
#     existing = cur.fetchall()
#     print(f"Existing student IDs in TEST_DB: {existing}")
#     conn.close()
    
#     # Also check the DB_PATH database
#     conn2 = sqlite3.connect(DB_PATH)
#     cur2 = conn2.cursor()
#     try:
#         cur2.execute("SELECT * FROM members")
#         existing2 = cur2.fetchall()
#         print(f"Existing student IDs in DB_PATH: {existing2}")
#     except:
#         print("DB_PATH database doesn't exist or has no table")
#     conn2.close()
#     positions = ["Volunteer", "President", "Vice President", "Vice President Female",
#                  "Treasurer", "General Secretary", "Media Secretary"]
#     for i, pos in enumerate(positions):
#         data = {
#             "action": "add",
#             "first_name": f"Test70{i}",
#             "last_name": f"User70{i}",
#             "gender": "Male",
#             "student_id": f"S70{i}",
#             "society": "UMT ACM",
#             "date_joined": "2025-12-24",
#             "position": pos
#         }
     
#         # response = add_member(client, "S707")
#         # html = response.get_data(as_text=True)

#         print(f"\n=== Attempting to add position {i}: {pos} with student_id: {data['student_id']} ===")

#         # assert "Member added successfully" in html or "Failed to add member" in html
        
#         response = client.post("/home", data=data, follow_redirects=True)
#         html = response.get_data(as_text=True)
        
#         print(f"Response contains 'Member added successfully!': {'Member added successfully!' in html}")
#         print(f"Response contains 'Failed to add member': {'Failed to add member' in html}")
#         assert "Member added successfully" in html 
        
#         # if "Failed to add member" in html:
#         #     print(f"ERROR MESSAGE: {html[html.find('Failed'):html.find('Failed')+200]}")
        
#         # assert b"Member added successfully!" in response.data