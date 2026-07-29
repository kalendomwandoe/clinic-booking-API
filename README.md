CLINIC BOOKING API
A backend API for managing doctors, working hours, and patient appointment bookings. 
It is built with FastAPI and PostgreSQL.


Live URL: https://clinic-booking-api-noc4.onrender.com


*DESIGN DECISIONS

1. Framework
FastAPI was chosen over Django for its lower ceremony. Compared to Django, it requires less setup for API-only projects, allowing me to focus more on implementing business logic than framework configuration.
It offers excellent performance, automatic interactive documentation, built-in request validation, and a clean, modern development experience.

2. Database layer
PostgreSQL with SQLAlchemy as the ORM.
I chose PostgreSQL because it's a reliable, feature-rich relational database that handles complex queries, transactions, and data integrity well, making it ideal for booking systems. I paired it with SQLAlchemy because it provides a clean ORM for working with Python objects instead of raw SQL, while still offering the flexibility to write optimized SQL queries when needed.

3. Core models
Doctor, WorkingHours, and Appointment (slot/booking), with appointment status tracking to support cancellation and rescheduling.

4. Shared booking validation
The reschedule endpoint reuses the same conflict-check logic as the create-appointment endpoint rather than duplicating it, since a reschedule is effectively "validate as a fresh booking" against existing slots.

5. Used SQLAlchemy's create_all() at startup instead of Alembic migrations.
It allows the application to create the required tables automatically at startup, reducing setup time and making the project easier to run. While Alembic is the better choice for production systems with evolving schemas, create_all() keeps the development workflow simple and lets me focus on implementing and testing the core booking logic.


*AMBIGUOUS REQUIREMENTS AND DECISIONS MADE

1. The spec said the reschedule endpoint should "validate as a fresh booking" but didn't specify exactly what that meant in practice. I was torn between whether it needed its own separate validation rules or should reuse existing booking logic.

I made the decision to treat a reschedule as equivalent to creating a new booking against the requested slot, and refactored the conflict-check logic into a single shared function used by both POST /appointments and the reschedule endpoint, rather than writing a separate, possibly inconsistent check. 

2. The assessment didn't explicitly mandate a specific migration approach.

I made the decision to use SQLAlchemy's create_all() at startup instead of setting up Alembic migrations

*RUNNING LOCALLY

1. Clone the repo and install dependencies
git clone <repo-url>
   cd clinic-booking-api
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Set up environment variables 
Create a .env file with;
    DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<dbname>

3. Run the app
    uvicorn app.main:app --reload

4. Run test
    pytest
Tests run against an in-memory SQLite database, so no local Postgres setup is required just to run the test suite.

5. API docs
    Once running, interactive docs are available at http://localhost:8000/docs

*DEPLOYMENT & CI/CD

1. Branch that triggers deployment
    main. branch 
    Render is connected directly to the GitHub repository and auto-deploys on every push to main — this happens through Render's native GitHub integration, not through GitHub Actions.

2. CI pipeline
    .github/workflows/test.yml
    Runs the full pytest suite against an in-memory SQLite database on every pull request targeting main. A PR cannot be merged if its checks show failing tests.

3. Pipeline description
    The two pieces are split by responsibility.
    (i) GitHub Actions handles verification.
        It runs automated tests on every PR so problems are caught before merge
    (ii) Render handles deployment
            It watches main and deploys automatically whenever a PR is merged, without needing deployment steps duplicated inside the GitHub Actions workflow.


*AI REFLECTION AND USAGE
1. What did I use AI for across the four sections?
    (i)Design
        talked through the data model (doctors, working hours, slots/appointments, cancellation state) before writing any code.
    (ii)Build
        built all four endpoints collaboratively, with explanations of SQLAlchemy/FastAPI patterns along the way, coming from a Prisma/MERN background.
    (iii)Deploy
        set up the GitHub Actions test workflow and worked out how it fits alongside Render's auto-deploy.
    (iv)Throughout
        used it to debug real errors as they came up rather than generating code upfront and hoping it worked.

2. One example where an AI suggestion improved my work
    I asked AI to explain the reschedule endpoint requirement ("validate as a fresh booking"). It pointed out this needed the same conflict-check logic as the original create-appointment endpoint, rather than a separate check. Therefore I refactored booking validation into one shared function used by both endpoints instead of duplicating logic.

3. One example where AI output was wrong or incomplete, and how I caught it
    After a router refactor, create_all() (which creates the database tables) got silently dropped, and it wasn't caught in review. AI had said the app was working. It surfaced as a live 500 error in production when the API tried to query tables that didn't exist, which forced us to trace it back and find the missing call.

4. Two decisions I made without AI
    (i)Choosing create_all() over Alembic migrations. While Alembic is the better choice for production systems with evolving schemas, create_all() keeps the development workflow simple.
    (ii)Choosing SQLite (in-memory) over Postgres for the test suite. This came down to what I'd be comfortable maintaining and explaining afterward, which is a judgment call rather than a technical correctness question.