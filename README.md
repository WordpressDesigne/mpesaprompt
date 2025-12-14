# M-Pesa STK Push SaaS Platform

This is a multi-tenant SaaS platform that lets multiple businesses send M-Pesa STK push requests to their customers through a central system.

## Features

- Multi-tenant architecture
- Business and Admin dashboards
- STK Push integration
- Customer management
- Commission and Wallet system
- Excel export

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** React (JavaScript)
- **Database:** PostgreSQL

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- npm or yarn
- pip
- PostgreSQL (for production, SQLite for development)

### 1. Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the `backend` directory based on `.env.example`.
    ```
    # Flask
    FLASK_APP=manage.py
    FLASK_ENV=development
    SECRET_KEY=your-secret-key # Change this to a strong, random key

    # Database
    DATABASE_URL=sqlite:///app.db # For local development with SQLite
    # For PostgreSQL on Render: DATABASE_URL=postgresql://user:password@host:5432/database_name 
    # IMPORTANT: Replace 'user', 'password', 'host', '5432', and 'database_name' with your actual PostgreSQL credentials provided by Render. Do not leave 'port' as a literal string.

    # JWT
    JWT_SECRET_KEY=your-jwt-secret-key # Change this to a strong, random key

    # M-Pesa (for Daraja API integration)
    MPESA_CONSUMER_KEY=your-consumer-key
    MPESA_CONSUMER_SECRET=your-consumer-secret
    MPESA_SHORTCODE=your-shortcode
    MPESA_PASSKEY=your-passkey

    # Admin User (for initial setup)
    ADMIN_EMAIL=admin@example.com
    ADMIN_PASSWORD=adminpassword
    ```

5.  **Initialize and apply database migrations (local development only):**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```
    *Note: For Render deployment, migrations are handled automatically during startup.*

6.  **Create an admin user:**
    ```bash
    python create_admin.py
    ```

7.  **Run the Flask backend:**
    ```bash
    flask run
    ```
    The backend will typically run on `http://127.0.0.1:5000`.

### 2. Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend/client
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Run the React development server:**
    ```bash
    npm run dev
    ```
    The frontend will typically run on `http://localhost:5173`. It is configured to proxy API requests to the backend.

## Deployment on Render

This application is designed for deployment on Render.com.

### Backend (Flask) Deployment

1.  **Create a new Web Service on Render:**
    - Connect your Git repository.
    - Set the `Root Directory` to `backend`.
    - Choose `Python` as the `Runtime`.
    - **Build Command:** `pip install -r requirements.txt`
        *   **Details:** This command installs all the Python dependencies listed in `backend/requirements.txt` that are necessary for your Flask application to run.
    - **Start Command:** `flask db upgrade && gunicorn manage:app`
        *   **Details:** This command first executes `flask db upgrade`. This is crucial for automated migrations. It applies any pending database migrations, ensuring your production database schema is up-to-date. The `&&` operator ensures that `gunicorn manage:app` (which starts your Flask application using the Gunicorn WSGI HTTP server) only runs if the migrations are successful. This command effectively starts your Flask application and serves it to the web.
    - **Environment Variables:**
        *   Add environment variables as defined in your `.env.example` file.
        *   **`DATABASE_URL`**: This MUST be set to your PostgreSQL database connection string provided by Render or your external PostgreSQL provider. This is critical for connecting your Flask app to the production database.
        *   **`SECRET_KEY`**: A strong, randomly generated secret key for Flask sessions.
        *   **`JWT_SECRET_KEY`**: A strong, randomly generated secret key for JWT token signing.
        *   **`MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, `MPESA_PASSKEY`**: Your actual M-Pesa Daraja API credentials for production.
        *   **`ADMIN_EMAIL`, `ADMIN_PASSWORD`**: For the initial admin user.

### Frontend (React) Deployment

1.  **Create a new Static Site on Render:**
    - Connect your Git repository.
    - Set the `Root Directory` to `frontend/client`.
    - **Build Command:** `npm install && npm run build`
        *   **Details:** This command first installs all Node.js dependencies for your React application (`npm install`) and then builds the optimized production bundle of your React app (`npm run build`). The output of `npm run build` is typically a `dist` directory.
    - **Publish Directory:** `dist`
        *   **Details:** This tells Render where to find the static files generated by the build process that should be served to users.
    - **Environment Variables:**
        *   **`VITE_API_BASE_URL`**: This environment variable needs to point to the URL of your deployed Flask backend service on Render. You will need to replace the local `fetch('/some-endpoint')` calls in your frontend with `fetch(`${import.meta.env.VITE_API_BASE_URL}/some-endpoint')` to correctly point to your deployed backend.

## API Endpoints

### Authentication

-   `POST /signup`: Register a new business.
-   `POST /login`: Log in a business and get a JWT token.
-   `POST /admin/login`: Log in an admin and get a JWT token.

### Business Actions (require JWT)

-   `GET /dashboard`: Get business dashboard overview.
-   `POST /stk-push`: Send an M-Pesa STK push request.
-   `GET /customers`: Get a list of customers.
-   `GET /customers/export-excel`: Export customer data to Excel.
-   `GET /wallet`: Get wallet balance and commission history.
-   `POST /settings/update`: Update Daraja API keys and Till/Paybill numbers.

### Admin Actions (require Admin JWT)

-   `GET /admin/businesses`: View all registered businesses.
-   `POST /admin/suspend/<int:business_id>`: Suspend a business.
-   `POST /admin/reactivate/<int:business_id>`: Reactivate a business.
-   `GET /admin/transactions`: View all transactions.
-   `GET /admin/commissions`: View all commission ledger entries.
-   `POST /admin/set-commission`: Adjust global commission percentage.
-   `GET /admin/impersonate/<int:business_id>`: Get a JWT token to impersonate a business.
-   `GET /admin/customers/export-excel`: Export all customer data to Excel.