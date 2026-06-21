import sqlite3

conn = sqlite3.connect("gym.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_type TEXT NOT NULL,
    workout_date DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS exercise_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER,
    exercise_name TEXT,
    set_number INTEGER,
    weight REAL,
    reps INTEGER,
    FOREIGN KEY(workout_id) REFERENCES workouts(id)
)
""")

conn.commit()
conn.close()

print("Tables created")
