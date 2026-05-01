TaskFlow — Project Management System

  A full-stack web application for managing projects, tasks, teams, and
  evaluations with role-based access control.

------------------------------------------------------------------------

Tech Stack

  Layer         Technology           Purpose
  ------------- -------------------- -----------------------------
  Frontend      React 18 + Vite      UI & build tool
  Styling       Tailwind CSS         Utility-first dark UI
  Routing       React Router v6      Client-side navigation
  HTTP Client   Axios                API calls + JWT interceptor
  Backend       Python Flask         REST API server
  Auth          Flask-JWT-Extended   JWT authentication
  ORM           Flask-SQLAlchemy     Database management
  Database      SQLite               Embedded relational DB
  Password      Werkzeug (scrypt)    Secure password hashing
  Config        python-dotenv        Environment variables

------------------------------------------------------------------------

Project Structure

    taskflow/
    ├── backend/
    │   ├── app.py                  # Flask app factory & entry point
    │   ├── config.py               # Configuration (loads .env)
    │   ├── setup_db.py             # Database setup & seed script
    │   ├── requirements.txt        # Python dependencies
    │   ├── .env                    # Environment variables (SECRET_KEY, JWT_SECRET_KEY)
    │   ├── models/
    │   │   └── __init__.py         # SQLAlchemy models (User, Project, Task, etc.)
    │   ├── routes/
    │   │   ├── auth.py             # /api/auth/* endpoints
    │   │   ├── projects.py         # /api/projects/* endpoints
    │   │   ├── tasks.py            # /api/tasks/* endpoints
    │   │   └── dashboard.py        # /api/dashboard endpoint
    │   └── middleware/
    │       └── auth.py             # JWT decorators & get_current_user()
    │
    └── frontend/
        └── src/
            ├── main.jsx            # React entry point
            ├── App.jsx             # Router setup & protected routes
            ├── context/
            │   └── AuthContext.jsx # Auth state, login/logout, isAdmin
            ├── utils/
            │   └── api.js          # Axios instance with JWT interceptor
            └── pages/
                ├── Login.jsx
                ├── Register.jsx
                ├── Dashboard.jsx
                ├── Projects.jsx
                ├── ProjectDetail.jsx
                └── Tasks.jsx

------------------------------------------------------------------------

Database Models

User

  Field           Type          Notes
  --------------- ------------- ------------------
  id              Integer       Primary key
  name            String(100)   Required
  email           String(120)   Unique, required
  password_hash   String(256)   Scrypt hash
  role            String(20)    admin or member
  created_at      DateTime      Auto UTC

Project

  Field         Type          Notes
  ------------- ------------- -------------
  id            Integer       Primary key
  name          String(150)   Required
  description   Text          Optional
  owner_id      FK → User     Required
  created_at    DateTime      Auto UTC

ProjectMember

  Field        Type           Notes
  ------------ -------------- ----------------
  id           Integer        Primary key
  project_id   FK → Project   Cascade delete
  user_id      FK → User      Required
  joined_at    DateTime       Auto UTC

Task

  Field         Type           Notes
  ------------- -------------- ---------------------------
  id            Integer        Primary key
  title         String(200)    Required
  description   Text           Optional
  status        String(20)     todo / in_progress / done
  due_date      DateTime       Optional
  project_id    FK → Project   Cascade delete
  assigned_to   FK → User      Optional
  created_by    FK → User      Required
  is_overdue    Property       Computed — not stored

TaskEvaluation

  Field                Type        Notes
  -------------------- ----------- ---------------------------------
  id                   Integer     Primary key
  task_id              FK → Task   Unique (one per task)
  evaluator_id         FK → User   Required
  accuracy_score       Float       0–10
  completeness_score   Float       0–10
  composite_score      Property    accuracy×0.6 + completeness×0.4
  comments             Text        Optional

------------------------------------------------------------------------

API Endpoints

Auth — /api/auth

  Method   Endpoint    Description                Auth
  -------- ----------- -------------------------- --------------
  POST     /register   Register new user          Public
  POST     /login      Login, receive JWT         Public
  GET      /me         Get current user profile   JWT Required

Projects — /api/projects

  ------------------------------------------------------------------------
  Method          Endpoint            Description              Auth
  --------------- ------------------- ------------------------ -----------
  GET             /                   List projects (all for   JWT
                                      admin, member’s only for Required
                                      members)                 

  POST            /                   Create project           Admin Only
                                      (auto-adds owner as      
                                      member)                  

  GET             /:id                Project detail with      JWT
                                      members & tasks          Required

  PUT             /:id                Update project           Admin Only
                                      name/description         

  DELETE          /:id                Delete project and all   Admin Only
                                      related data             

  POST            /:id/members        Add a user as project    Admin Only
                                      member                   

  DELETE          /:id/members/:uid   Remove a member from     Admin Only
                                      project                  

  GET             /users              List all users (for      Admin Only
                                      member picker)           
  ------------------------------------------------------------------------

Tasks — /api/tasks

  ------------------------------------------------------------------------
  Method          Endpoint            Description              Auth
  --------------- ------------------- ------------------------ -----------
  GET             /                   List tasks (filtered by  JWT
                                      project/assignee)        Required

  POST            /                   Create new task          Admin Only

  GET             /:id                Get task detail with     JWT
                                      evaluation               Required

  PUT             /:id                Update task fields or    JWT
                                      status                   Required

  DELETE          /:id                Delete a task            Admin Only

  POST            /:id/evaluate       Submit or update task    Admin Only
                                      evaluation               
  ------------------------------------------------------------------------

Dashboard — /api/dashboard

  ------------------------------------------------------------------------
  Method          Endpoint            Description              Auth
  --------------- ------------------- ------------------------ -----------
  GET             /                   Stats: projects, tasks,  JWT
                                      members, overdue count   Required

  ------------------------------------------------------------------------

------------------------------------------------------------------------

Authentication & Security

JWT Flow

1.  User submits credentials → POST /api/auth/login
2.  Backend verifies password hash (Werkzeug scrypt)
3.  Flask-JWT-Extended issues token — identity = str(user.id)
4.  Frontend stores token in localStorage via AuthContext.login()
5.  Axios interceptor attaches Authorization: Bearer <token> to every
    request
6.  Backend decorators verify_jwt_in_request() and admin_required() gate
    all protected routes

Role-Based Access Control

  -----------------------------------------------------------------------
  Role                    Permissions
  ----------------------- -----------------------------------------------
  Admin                   Full CRUD on projects, tasks, members,
                          evaluations. Access to all endpoints.

  Member                  View assigned projects & tasks only. Can update
                          task status. No admin routes.
  -----------------------------------------------------------------------

Security Measures

-   Passwords hashed using Werkzeug scrypt (never stored plain text)
-   JWT secret key must be 32+ bytes (RFC 7518 HS256 requirement)
-   JWT identity stored as string to comply with RFC 7519
-   Admin role verified server-side on every protected request
-   CORS configured with flask-cors

------------------------------------------------------------------------

Setup & Installation

Prerequisites

-   Python 3.10+
-   Node.js 18+
-   Git

------------------------------------------------------------------------

Backend Setup

    # 1. Navigate to backend
    cd taskflow/backend

    # 2. Create and activate virtual environment
    python -m venv venv
    venv\Scripts\activate        # Windows
    source venv/bin/activate     # Mac/Linux

    # 3. Install dependencies
    pip install -r requirements.txt

    # 4. Generate strong secret keys
    python -c "import secrets; print(secrets.token_hex(32))"
    # Run twice — one for SECRET_KEY, one for JWT_SECRET_KEY

Create .env file in /backend:

    SECRET_KEY=<your_32_byte_hex_key>
    JWT_SECRET_KEY=<your_32_byte_hex_key>
    DATABASE_URL=sqlite:///local.db
    FLASK_DEBUG=True

    # 5. Setup and seed database
    python setup_db.py

    # 6. Start Flask server
    python app.py
    # Runs on: http://127.0.0.1:5000

------------------------------------------------------------------------

Frontend Setup

    # 1. Navigate to frontend
    cd taskflow/frontend

    # 2. Install dependencies
    npm install

    # 3. Create .env file
    echo "VITE_API_URL=http://127.0.0.1:5000/api" > .env

    # 4. Start dev server
    npm run dev
    # Runs on: http://localhost:5173

------------------------------------------------------------------------

Reset Database

    # Wipe all data and reseed from scratch
    python setup_db.py --reset

------------------------------------------------------------------------

Default Login Credentials

  Available after running python setup_db.py

  Role     Email                Password
  -------- -------------------- ----------
  Admin    admin@taskflow.com   admin123
  Member   alice@taskflow.com   alice123
  Member   bob@taskflow.com     bob123

------------------------------------------------------------------------

Environment Variables Reference

  -----------------------------------------------------------------------
  Variable              Required              Description
  --------------------- --------------------- ---------------------------
  SECRET_KEY            Yes (backend)         Flask session secret — must
                                              be 32+ bytes

  JWT_SECRET_KEY        Yes (backend)         JWT signing key — must be
                                              32+ bytes

  DATABASE_URL          Yes (backend)         SQLAlchemy URI — default
                                              sqlite:///local.db

  FLASK_DEBUG           No                    Enable debug mode — set
                                              True for development

  VITE_API_URL          Yes (frontend)        Backend API base URL
  -----------------------------------------------------------------------

------------------------------------------------------------------------

Known Issues Fixed

1. JWT Identity Type Mismatch

Problem: create_access_token(identity=user.id) passed an integer.
Flask-JWT-Extended requires a string identity (RFC 7519), causing
Subject must be a string and 401 on all requests.
Fix: Changed to create_access_token(identity=str(user.id)) and updated
get_current_user() to cast back with int(get_jwt_identity()).

2. Redundant Authorization Header

Problem: Projects.jsx was manually passing Authorization header in
api.post(), conflicting with the global Axios interceptor.
Fix: Removed manual header — simplified to
await api.post('/projects', form).

3. Wrong POST Route Path

Problem: Create project route was
@projects_bp.route('/project', methods=['POST']) — making it unreachable
at POST /api/projects.
Fix: Changed to @projects_bp.route('', methods=['POST']).

4. Weak JWT Secret Key

Problem: .env had placeholder keys below the 32-byte minimum for HS256,
causing InsecureKeyLengthWarning and token rejections.
Fix: Generated cryptographically secure keys using
secrets.token_hex(32).

------------------------------------------------------------------------

Features Summary

-   JWT authentication with secure token lifecycle
-   Role-based access control (Admin / Member)
-   Project creation, update, deletion with cascade
-   Automatic owner membership on project creation
-   Task management with status tracking (Todo → In Progress → Done)
-   Overdue task detection via computed is_overdue property
-   Task evaluation with accuracy + completeness scoring and composite
    score
-   Admin dashboard with system-wide statistics
-   Responsive dark UI with Tailwind CSS
-   Axios interceptor for automatic token attachment on all requests
