# Mini Pluggable Data Transformer (FastAPI)

This project is a lightweight and extensible web server that accepts datasets (CSV or JSON), applies a configurable pipeline of data transformations, and returns the result as JSON. It supports role-based user access and transformation registration.

---

## Features

- Accepts both CSV file uploads and raw JSON data.
- Supports pluggable transformation pipelines (e.g., filter, rename, uppercase, sort, etc.).
- Users are authenticated using JWT tokens.
- Admin users can configure which transformations are available to each user.
- All transformers are registered in a central registry and validated before execution.
- MongoDB is used as the backend database.
- Rate limiting is enforced for all routes.
- Transformers can validate arguments and expected column types in advance.
- Admin user will be created if there is no previously created admin user.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/dinhlongviolin1/data-transformer.git
cd data-transformer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup environment variables

Create a `.env` file in the project root:

```
MONGO_URI=mongodb+srv://
SECRET_KEY=my-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
RATE_LIMIT=20/minute
DEFAULT_TRANSFORMS=uppercase,rename
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
```

If any environment variable is missing, a default will be used with a warning printed.

### 4. Run the application

```bash
fastapi dev main.py
```

Server will run at: <http://localhost:8000>

---

## API Usage

### Authentication

- `POST /auth/login`  
  Request: `{ "username": "user", "password": "pass" }`  
  Response: `{ "access_token": "<token>" }`

- `POST /auth/register`  
  Create new user and assign default allowed transformers.

---

### Transform endpoints

- `POST /transform/`  
  Accepts JSON data and transformation pipeline.

  Request:

  ```json
  {
    "data": [{ "name": "Alice", "score": 80 }],
    "pipeline": [{ "name": "uppercase", "args": { "column": "name" } }]
  }
  ```

- `POST /transform/file`  
  Accepts CSV file and pipeline string (JSON array) using multipart/form-data.  
  Fields:

  - `file`: CSV file
  - `pipeline`: JSON string of steps

- `GET /transform/`  
  Returns list of transformers available to the current user, including required arguments and expected column types.

- `PUT /transform/user/{username}`  
  (Admin user only) Set allowed transformers for a user. Body: `["filter", "rename", "uppercase"]`

---

## Transformers

Each transformer requires specific arguments. Built-in examples:

- `filter`: Filter rows with condition (e.g., `score > 90`)
- `rename`: Rename a column
- `uppercase`: Uppercase all values in a column
- `drop`: Drop columns from dataset
- `fillna`: Fill missing values
- `sort`: Sort by column

Each transformer performs input validation before execution.
