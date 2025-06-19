import os

from cs50 import SQL
from datetime import datetime, timezone
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///exa.db")


# Custom Jinja filter for formatting datetime
def format_datetime_display(value, format='%Y-%m-%d %I:%M %p'):
    """Formats an ISO datetime string or datetime object for display."""
    if not value:
        return ""
    if isinstance(value, str):
        try:
            # Ensure parsing from ISO format which we store
            dt_obj = datetime.fromisoformat(value)
        except ValueError:
            return value # Return original if parsing fails
    elif isinstance(value, datetime):
        dt_obj = value
    else:
        return value # Should not happen if data is consistent

    # Convert to local timezone if it's timezone-aware and in UTC
    # For simplicity here, we assume stored times are meant as 'local' or naive.
    # If you store UTC, you'd convert to user's local timezone here.
    return dt_obj.strftime(format)

app.jinja_env.filters['datetime_display'] = format_datetime_display

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Authentication routes
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out."""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 403)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        # Hash the password
        hash = generate_password_hash(request.form.get("password"))

        # Insert new user into database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hash)

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    

# CORE APPLICATION ROUTES
@app.route("/subjects", methods=["GET", "POST"])
@login_required
def subjects():
    """Manage subjects"""
    user_id = session["user_id"]

    if request.method == "POST":
        # Add a new subject
        subject_name = request.form.get("subject_name")
        if not subject_name:
            return apology("must provide subject name", 400)

        # Insert the subject into the database
        try:
            db.execute("INSERT INTO subjects (user_id, name) VALUES (?, ?)", user_id, subject_name)
            flash("Subject added successfully!", "success")
        except:
            return apology("subject already exists", 400)

        # Redirect back to the subjects page
        return redirect("/subjects")

    else:
        # Fetch all subjects for the user
        subjects = db.execute("SELECT * FROM subjects WHERE user_id = ?", user_id)
        return render_template("subjects.html", subjects=subjects)


@app.route("/delete_subject/<int:subject_id>", methods=["POST"])
@login_required
def delete_subject(subject_id):
    """Delete a subject"""
    user_id = session["user_id"]

    # Ensure the subject belongs to the user
    db.execute("DELETE FROM subjects WHERE id = ? AND user_id = ?", subject_id, user_id)
    flash("Subject deleted successfully!", "success")

    # Redirect back to the subjects page
    return redirect("/subjects")



@app.route("/index", methods=["GET", "POST"])
def index():
    if not session.get("user_id"):
        return redirect("/login")
    user_id = session["user_id"]
    if request.method == "POST":
        subject_id_str = request.form.get("subject_id")
        start_time_str = request.form.get("start_time") # Expected format: YYYY-MM-DDTHH:MM
        end_time_str = request.form.get("end_time")     # Expected format: YYYY-MM-DDTHH:MM
        notes = request.form.get("notes", "").strip()

        # Validate inputs
        if not subject_id_str or not subject_id_str.isdigit():
            return apology("Invalid subject selected.", 400)
        subject_id = int(subject_id_str)

        if not start_time_str or not end_time_str:
            return apology("Start and end times are required.", 400)

        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
            return apology("Invalid date/time format.", 400)

        if end_time <= start_time:
            return apology("End time must be after start time.", 400)

        duration_delta = end_time - start_time
        duration_minutes = int(duration_delta.total_seconds() / 60)

        if duration_minutes <= 0:
            return apology("Session duration must be positive.", 400)

        # Verify subject belongs to user (important!)
        subject = db.execute("SELECT id FROM subjects WHERE id = ? AND user_id = ?", subject_id, user_id)
        if not subject:
            return apology("Invalid subject selected or subject does not belong to you.", 403)

        try:
            db.execute("""
                INSERT INTO study_sessions (user_id, subject_id, start_time, end_time, duration_minutes, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, user_id, subject_id, start_time.isoformat(), end_time.isoformat(), duration_minutes, notes)
                
            flash(f"Study session logged successfully!", "success")
        except Exception as e:
            return apology(f"Failed to log session: {str(e)}", 500)
        
        return redirect("/")

    else: # GET request
        # Fetch user's subjects for the dropdown
        subjects = db.execute("SELECT id, name FROM subjects WHERE user_id = ? ORDER BY name", user_id)
        return render_template("index.html", subjects=subjects)

# LANDING PAGE ROUTE (for not logged in users)
@app.route("/landing")
def landing():
    # If logged in, redirect to main page
    if session.get("user_id"):
        return redirect("/")
    return render_template("landing.html")

# OVERRIDE ROOT ROUTE TO SHOW LANDING IF NOT LOGGED IN OR INDEX IF LOGGED IN
@app.route("/", methods=["GET", "POST"])
def root():
    if session.get("user_id"):
        return index()
    return render_template("landing.html")


@app.route("/history")
@login_required
def history():
    """Show history of study sessions"""
    user_id = session["user_id"]
    
    # Get filter parameters (if any)
    subject_id = request.args.get("subject_id")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    
    # Base query to join study_sessions with subjects to get subject names
    base_query = """
        SELECT 
            ss.id, 
            ss.start_time, 
            ss.end_time, 
            ss.duration_minutes, 
            ss.notes, 
            s.name as subject_name,
            s.id as subject_id
        FROM study_sessions ss
        JOIN subjects s ON ss.subject_id = s.id
        WHERE ss.user_id = ?
    """
    query_params = [user_id]
    
    # Add filters if provided
    if subject_id and subject_id.isdigit():
        base_query += " AND ss.subject_id = ?"
        query_params.append(int(subject_id))
        
    if date_from:
        try:
            # Convert to datetime object and back to ISO for consistent formatting
            date_from_obj = datetime.fromisoformat(date_from)
            base_query += " AND ss.start_time >= ?"
            query_params.append(date_from_obj.isoformat())
        except ValueError:
            # If invalid date, ignore this filter
            pass
            
    if date_to:
        try:
            # Convert to datetime object and back to ISO for consistent formatting
            date_to_obj = datetime.fromisoformat(date_to)
            base_query += " AND ss.end_time <= ?"
            query_params.append(date_to_obj.isoformat())
        except ValueError:
            # If invalid date, ignore this filter
            pass
    
    # Order by most recent sessions first
    base_query += " ORDER BY ss.start_time DESC"
    
    # Execute the query
    sessions = db.execute(base_query, *query_params)
    
    # Calculate total study time
    total_duration = sum(session["duration_minutes"] for session in sessions)
    
    # Format the total duration as hours and minutes
    total_hours = total_duration // 60
    total_minutes = total_duration % 60
    
    # Get all subjects for the filter dropdown
    subjects = db.execute("SELECT id, name FROM subjects WHERE user_id = ? ORDER BY name", user_id)
    
    # Calculate subject-wise statistics for the chart
    subject_stats = db.execute("""
        SELECT 
            s.name as subject_name, 
            SUM(ss.duration_minutes) as total_minutes
        FROM study_sessions ss
        JOIN subjects s ON ss.subject_id = s.id
        WHERE ss.user_id = ?
        GROUP BY ss.subject_id
        ORDER BY total_minutes DESC
    """, user_id)
    
    return render_template(
        "history.html", 
        sessions=sessions, 
        subjects=subjects,
        subject_stats=subject_stats,
        total_hours=total_hours,
        total_minutes=total_minutes,
        selected_subject_id=subject_id,
        date_from=date_from,
        date_to=date_to
    )


@app.route("/delete_session/<int:session_id>", methods=["POST"])
@login_required
def delete_session(session_id):
    """Delete a study session"""
    user_id = session["user_id"]

    try:
        # First check if the session exists and belongs to the user
        result = db.execute(
            "SELECT id FROM study_sessions WHERE id = ? AND user_id = ?", 
            session_id, 
            user_id
        )
        
        if not result:
            flash("Session not found or you don't have permission to delete it", "error")
            return redirect("/history")
        
        # If we found the session and it belongs to the user, delete it
        db.execute(
            "DELETE FROM study_sessions WHERE id = ? AND user_id = ?", 
            session_id, 
            user_id
        )
        
        flash("Study session deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting session: {str(e)}", "error")
    
    # Get the referrer URL or default to history
    return_url = request.referrer or "/history"
    return redirect(return_url)


if __name__ == "__main__":
    # For development, FLASK_ENV=development and FLASK_DEBUG=1 are usually set as environment variables
    # The CS50 IDE often handles this. For local run:
    app.run(debug=True)