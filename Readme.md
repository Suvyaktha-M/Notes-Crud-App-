# Notes CRUD App

A web-based application for creating, organizing, searching, editing, and deleting notes. Built using Python and Flask, with SQLite for data storage and HTML/CSS for the user interface.

## Features

- **Create Notes:** Add notes with a title, content, and category.
- **View Notes:** Display saved notes in the application.
- **Edit Notes:** Update existing note details.
- **Delete Notes:** Remove notes with a confirmation step.
- **Search Notes:** Search by title or content.
- **Category Filtering:** Filter notes by Personal, Study, Work, or Other.
- **Timestamps:** Track when notes were created and last updated.
- **REST API:** Perform CRUD operations through HTTP endpoints.
- **Persistent Storage:** Store notes in an SQLite database.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Web framework and REST API |
| SQLite | Database |
| HTML | Page structure |
| CSS | Styling and responsive layout |

## Project Structure

```text
Notes CRUD App/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   └── style.css
└── templates/
    ├── index.html
    ├── edit.html
    └── confirm_delete.html
```

The SQLite database is created automatically when the application starts. The `.venv/` folder contains the local Python virtual environment and is not included in the repository.

## Installation and Setup

### Prerequisites
- Python 3 installed
- Git (if cloning the repository)

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd "Notes CRUD App"
```

### 2. Create a Virtual Environment

```bash
py -m venv .venv
```

### 3. Activate the Environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

## REST API Endpoints

| HTTP Method | Endpoint | Description |
|---|---|---|
| GET | `/api/notes` | Retrieve all notes |
| GET | `/api/notes/<id>` | Retrieve a specific note |
| POST | `/api/notes` | Create a note |
| PUT | `/api/notes/<id>` | Update a note |
| DELETE | `/api/notes/<id>` | Delete a note |

## Database

The application uses SQLite to store notes. The database is initialized automatically when `app.py` runs. Existing local database files are not required in the GitHub repository.