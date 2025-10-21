# String Analyzer API — Backend Wizards (Stage 1)

A RESTful API built with **Django REST Framework** that analyzes strings and stores their metadata (length, palindrome status, word count, character frequency, and hash).  
This project fulfills the Stage 1 requirements for the **Backend Wizards** program.

---

## Features

- Create and analyze any string dynamically  
- Retrieve all analyzed strings  
- Filter results by min/max length, palindrome status, or date range  
- Get specific string details by value  
- Delete a string  
- Clean JSON responses per task spec

---

## Tech Stack

- **Python 3.10+**
- **Django 5+**
- **Django REST Framework**
- **SQLite3 (default DB)** — can switch to PostgreSQL/MySQL easily
- **Requests** (optional, for external integration)

---

## Installation & Setup

### 1Clone the Repository
```bash
git clone https://github.com/<olumbah1>/string-analyzer-api.git
cd string-analyzer-api
