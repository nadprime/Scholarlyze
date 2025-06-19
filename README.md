# Scholarlyze

Scholarlyze is a personal study tracker web application designed to help users log their study sessions, manage subjects, and visualize their progress. Built using Flask, it provides an intuitive interface for tracking academic efforts and improving productivity.

## Features

- **User Authentication**: Secure login and registration system.
- **Subject Management**: Add, view, and delete subjects.
- **Study Session Logging**: Log study sessions with details such as subject, start time, end time, duration, and optional notes.
- **History and Statistics**: View study history, filter sessions by subject or date, and analyze subject-wise study time.
- **Responsive Design**: Mobile-friendly interface using Bootstrap.

## Video

Project Demo: https://youtu.be/4zcWylWrL7Y

## Screenshots

![ss1](https://github.com/user-attachments/assets/d1700963-fe37-4ca1-8dd7-026eda49cbf3)

![ss2](https://github.com/user-attachments/assets/45e6c583-97cf-4df6-8e95-3b5d4a963624)

![ss3](https://github.com/user-attachments/assets/5904f002-4ffd-40e9-96af-cbd6f11c0dd2)

![ss4](https://github.com/user-attachments/assets/8c9babdc-82fa-427c-b951-b4e887e5bb3d)

![ss5](https://github.com/user-attachments/assets/6a09b5c4-cf14-4315-b6b2-b7d980583e57)

![ss6](https://github.com/user-attachments/assets/979384b2-a731-40ac-90f9-024148277bb4)


## Technologies Used

- **Backend**: Flask
- **Database**: SQLite (via CS50 SQL library)
- **Frontend**: HTML, CSS, Bootstrap
- **Session Management**: Flask-Session
- **Other Libraries**: Werkzeug, pytz, requests

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd project
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   sqlite3 studylog.db < query.sql
   ```

5. Run the application:
   ```bash
   flask run
   ```

## Usage

1. **Register**: Create an account to start using Scholarlyze.
2. **Log In**: Access your dashboard after logging in.
3. **Manage Subjects**: Add subjects to organize your study sessions.
4. **Log Sessions**: Record study sessions with details like subject, time, and notes.
5. **View History**: Analyze your study history and filter sessions by subject or date.

## Folder Structure

```
project/
├── app.py                # Main application file
├── requirements.txt      # Python dependencies
├── query.sql             # Database schema
├── templates/            # HTML templates
│   ├── layout.html       # Base layout template
│   ├── index.html        # Log study session page
│   ├── subjects.html     # Manage subjects page
│   ├── history.html      # Study history page
│   ├── login.html        # Login page
│   ├── register.html     # Register page
│   ├── landing.html      # Landing page for non-logged-in users
│   ├── error.html        # Generic error page
│   └── apology.html      # Apology page for errors
└── static/               # Static files (CSS, JS, images)
```

## Acknowledgments
- Built using Flask and Bootstrap.
