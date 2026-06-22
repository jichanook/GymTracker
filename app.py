from flask import Flask, render_template, request, redirect
from flask import session
import sqlite3

app = Flask(__name__)

app.secret_key = "gymtracker-secret-key"

WORKOUTS = {

"Upper A": {
    "Incline DB Press": 4,
    "Machine Chest Press": 3,
    "Shoulder Press": 3,
    "Cable Lateral Raise": 4,
    "Tricep Pushdown": 3,
    "Overhead Tricep Extension": 3
},

"Lower A": {
    "Back Squat": 4,
    "Romanian Deadlift": 4,
    "Bulgarian Split Squat": 3,
    "Leg Curl": 3,
    "Standing Calf Raise": 4,
    "Hanging Leg Raise": 3
},

"Upper B": {
    "Pull Ups": 4,
    "Single Arm Cable Pulldown": 3,
    "Chest Supported Row": 4,
    "Face Pull": 3,
    "Incline DB Curl": 3,
    "Hammer Curl": 3,
    "Cable Lateral Raise": 3
},

"Lower B": {
    "Leg Press": 4,
    "Walking Lunges": 3,
    "Leg Curl": 3,
    "Cable Lateral Raise": 4,
    "Rear Delt Fly": 3,
    "EZ Curl": 3,
    "Skull Crusher": 3
}

}

# login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user_id = int(
            request.form["user_id"]
        )

        session["user_id"] = user_id

        if user_id == 1:
            session["username"] = "Lotte"
        else:
            session["username"] = "Jay"

        return redirect("/")

    return render_template("login.html")

# logout
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# Database helper
def get_db():
    conn = sqlite3.connect("gym.db")
    conn.row_factory = sqlite3.Row
    return conn

# Home page
@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("home.html")

# Weigh-in page
@app.route("/weighin", methods=["GET", "POST"])
def weighin():

    if request.method == "POST":

        weight = request.form["weight"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO weighins
            (
                weight,
                user_id
            )
            VALUES (?, ?)
            """,
            (
                weight,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("weighin.html")

# Workout page
@app.route("/workout")
def workout():

    return render_template(
        "workout_select.html",
        workouts=WORKOUTS.keys()
    )

# workout logging
@app.route("/workout/<workout_type>")
def workout_page(workout_type):

    exercises = WORKOUTS[workout_type]

    conn = get_db()
    cursor = conn.cursor()

    previous_data = {}

    cursor.execute("""
        SELECT id
        FROM workouts
        WHERE workout_type = ?
        AND user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """,
    (
        workout_type,
        session["user_id"]
    ))

    last_workout = cursor.fetchone()

    if last_workout:

        cursor.execute("""
            SELECT *
            FROM exercise_sets
            WHERE workout_id = ?
            ORDER BY exercise_name, set_number
        """, (last_workout["id"],))

        sets = cursor.fetchall()

        for s in sets:

            exercise = s["exercise_name"]

            if exercise not in previous_data:
                previous_data[exercise] = []

            previous_data[exercise].append(
                f'{s["weight"]} x {s["reps"]}'
            )

    conn.close()

    return render_template(
        "workout.html",
        workout_type=workout_type,
        exercises=exercises,
        previous_data=previous_data
    )

# save workout route
@app.route("/save_workout", methods=["POST"])
def save_workout():

    workout_type = request.form["workout_type"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO workouts
        (
            workout_type,
            user_id
        )
        VALUES (?, ?)
        """,
        (
            workout_type,
            session["user_id"]
        )
    )

    workout_id = cursor.lastrowid

    for exercise in WORKOUTS[workout_type]:

        for set_num in range(1,5):

            weight = request.form.get(
                f"{exercise}_weight_{set_num}"
            )

            reps = request.form.get(
                f"{exercise}_reps_{set_num}"
            )

            if weight and reps:

                cursor.execute(
                    """
                    INSERT INTO exercise_sets
                    (
                    workout_id,
                    exercise_name,
                    set_number,
                    weight,
                    reps
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        workout_id,
                        exercise,
                        set_num,
                        weight,
                        reps
                    )
                )

    conn.commit()
    conn.close()

    return render_template("saved.html")

# History page
@app.route("/history")
def history():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM weighins
    WHERE user_id = ?
    ORDER BY timestamp DESC
    """, (session["user_id"],))

    weights = cursor.fetchall()

    cursor.execute("""
    SELECT *
    FROM workouts
    WHERE user_id = ?
    ORDER BY workout_date DESC
    """, (session["user_id"],))

    workouts = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        weights=weights,
        workouts=workouts
    )

# workout history
@app.route("/workout_history/<int:workout_id>")
def workout_history(workout_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM workouts
        WHERE id = ?
    """, (workout_id,))

    workout = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM exercise_sets
        WHERE workout_id = ?
        ORDER BY exercise_name, set_number
    """, (workout_id,))

    sets = cursor.fetchall()

    conn.close()

    exercises = {}

    for s in sets:

        exercise = s["exercise_name"]

        if exercise not in exercises:
            exercises[exercise] = []

        exercises[exercise].append(
            f'{s["weight"]}kg × {s["reps"]}'
        )

    return render_template(
        "workout_history.html",
        workout=workout,
        exercises=exercises
    )

if __name__ == "__main__":
    app.run(
    host="0.0.0.0",
    port=5000,
    debug=True
)
