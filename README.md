# Python + Angular Project

This project is a **full-stack application** with a Python backend (Flask) and an Angular frontend.  
It allows users to interact with a chatbot, manage health data, and view information through a user-friendly interface.

---

## Features

- Chatbot interface for user queries  
- Health data tracking and display  
- Responsive Angular frontend  
- Python Flask backend API  

---

## Installation

### Clone the repository
```bash
git clone https://github.com/Aditik081/pyhtonpro.git
cd pyhtonpro

# Create virtual environment
python -m venv env

# Activate environment (Windows PowerShell)
.\env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

cd frontend

# Install node dependencies
npm install

# Serve Angular app
ng serve

pyhtonpro/
├─ app.py                  # Python backend entry point
├─ frontend/               # Angular frontend
│  ├─ src/
│  ├─ package.json
│  └─ angular.json
├─ .gitignore
└─ README.md

#LICENSE
This project is licensed under the **MIT License**.

# Run the backend server
python app.py
