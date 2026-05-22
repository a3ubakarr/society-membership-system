import sqlite3
from ..models.db_init import DB_PATH

def get_db():
    return sqlite3.connect(DB_PATH)

def add_member(data):
    """
    Add a new member.
    Data tuple: (first, last, gender, student_id, society, date_joined, position)
    """
    conn = get_db()
    cur = conn.cursor()

    # ✅ Check duplicate student_id
    cur.execute("SELECT 1 FROM members WHERE student_id = ?", (data[3],))
    if cur.fetchone():
        conn.close()
        raise ValueError("Failed to add member")

    # Insert if not duplicate
    cur.execute("""
        INSERT INTO members
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()


def find_by_student_id(student_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM members WHERE student_id=?", (student_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def find_by_society(society):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM members WHERE society_name=?", (society,))
    rows = cur.fetchall()
    conn.close()
    return rows

def update_member(student_id, data):
    """
    Update a member using student_id
    data tuple: (first_name, last_name, gender, society_name, date_joined, position)
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE members
        SET first_name = ?,
            last_name = ?,
            gender = ?,
            society_name = ?,
            date_joined = ?,
            position = ?
        WHERE student_id = ?
    """, data + (student_id,))
    
    if cur.rowcount == 0:
        conn.close()
        raise ValueError(f"No member found with student_id '{student_id}'")

    conn.commit()
    conn.close()
    
def delete_member(student_id):
    """
    Delete a member using student_id.
    Raises ValueError if student_id does not exist.
    """
    conn = get_db()
    cur = conn.cursor()

    # Execute deletion
    cur.execute("DELETE FROM members WHERE student_id = ?", (student_id,))

    # Check if any row was actually deleted
    if cur.rowcount == 0:
        conn.close()
        raise ValueError(f"No member found with student_id '{student_id}'")

    conn.commit()
    conn.close()


def count_members_by_society():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT society_name, COUNT(*)
        FROM members
        GROUP BY society_name
    """)

    data = cur.fetchall()
    conn.close()
    return data
   


