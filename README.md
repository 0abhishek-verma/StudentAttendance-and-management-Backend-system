# Student Attendance and Management Backend System

This is a Django REST Framework-based backend project designed to manage student attendance and task submissions. The system provides APIs for both admin and student users. Admins can manage student profiles, assign tasks, track submissions, and generate attendance reports. Students can mark their attendance and submit assigned tasks.

## Features

- Admin can:
  - Create and manage student accounts
  - Assign tasks to individual students
  - View submitted tasks and score them
  - Monitor and export attendance data as CSV

- Students can:
  - Mark attendance once per day
  - View assigned tasks
  - Submit completed tasks for review

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite (default) or MySQL (optional)

## Getting Started

1. **Clone the Repository**

git clone https://github.com/0abhishek-verma/StudentAttendance-and-management-Backend-system.git
cd StudentAttendance-and-management-Backend-system


2. **Create a Virtual Environment and Activate**
pip install -r requirements.txt

3. **Install Dependencies**
python manage.py makemigrations
python manage.py migrate


5. **Create Superuser (Admin Account)**
python manage.py createsuperuser


6. **Run the Development Server**
python manage.py runserver


## Basic API Endpoints

- `POST /api/register/` – Register new user (student)
- `POST /api/login/` – Login user
- `POST /api/attendance/mark/` – Mark daily attendance
- `GET /api/attendance/report/` – View attendance (admin only)
- `POST /api/tasks/assign/` – Assign tasks (admin only)
- `POST /api/tasks/submit/<task_id>/` – Submit task (student)
- `GET /api/tasks/submissions/` – View submissions

> Authentication is required for most endpoints.

## Future Enhancements

- JWT authentication
- Dashboard interface integration
- Task deadlines and reminders
- PDF report generation

## License

This project is open-source and available under the [MIT License](LICENSE).

## Author

**Abhishek Verma**  
GitHub: [@0abhishek-verma](https://github.com/0abhishek-verma)

