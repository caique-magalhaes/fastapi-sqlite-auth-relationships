![Tests](https://github.com/caique-magalhaes/fastapi-sqlite-auth-relationships/actions/workflows/test.yml/badge.svg)


# 🚀 Robust RESTful Post Management API

A high-performance, fully authenticated CRUD API built with **FastAPI** and **SQLAlchemy**. This project was engineered using **Extreme Programming (XP)** methodologies and strict **Test-Driven Development (TDD)** practices to guarantee production stability and bulletproof authorization guardrails.

---

## 🛠️ Tech Stack & Architecture

- **Backend Framework:** FastAPI (Python)
- **Database ORM:** SQLAlchemy (Relational Database Mapping)
- **Data Validation:** Pydantic
- **Testing Engine:** Pytest

### Architectural Patterns Applied:
- **Separation of Concerns:** Clear isolation between the routing layer (`main.py`) and the database execution logic (`crud.py`).
- **Defensive Programming:** Thorough handling of edge cases, token validation, and resource availability before executing database writes.

---

## ✨ Core Features & Security Boundaries

- **Full CRUD Operations:** Securely create, read, update, and delete resource posts.
- **Bearer Token Authentication:** Endpoint protection driven by secure JWT token validation layers.
- **Strict Authorization Guards (Multi-Tenant Security):** Implements absolute cross-user protection. Users are completely restricted from modifying or deleting posts owned by other accounts, securely returning standard HTTP `403 Forbidden` responses.
- **Robust Exception Handling:** Clear, structured API responses for missing resources (`404 Post not Found`), missing credentials (`401 Unauthorized`), or permission violations (`403 Forbidden`).

---

## 🧪 Test-Driven Development (TDD) Suite

This project maintains a robust integration test suite built with `pytest` to simulate live API interactions and strictly enforce security rules.

To execute the test suite locally:
```bash
pytest
```

## Clone the repository:
```bash
git clone https://github.com/caique-magalhaes/fastapi-sqlite-auth-relationships.git 
cd fastapi-sqlite-auth-relationships
```

### Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Launch the API server:
```bash
uvicorn main:app --reload
```
