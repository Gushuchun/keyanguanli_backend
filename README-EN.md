# Research Management Platform - Backend Project

## 1. Project Introduction
This project is the backend system of a Research Management Platform, developed using the Django framework. It aims to provide efficient management tools for research teams. The system supports user management, team management, competition management, and other features to help research teams collaborate and manage projects better.

## 2. Feature Overview
- **User Management**: Supports user registration, login, and information management, including students, teachers, and team leaders.
- **Team Management**: Supports team creation, member invitations, team management, including team information updates, and team dissolution.
- **Competition Management**: Supports competition creation, updating competition information, deleting competitions, and managing competition results.
- **Permission Management**: Supports role-based permission management for different user roles, such as students, teachers, and team administrators.

## 3. Module Overview

### 1. User Module
- **Function**: User registration, login, and information management.
- **API Endpoints**:
  - `POST /api/user/register/`: User registration
    - **Parameters**:
      - `role`: User role, possible values are `student` or `teacher`
      - `username`: Username
      - `password`: Password
      - `college_id`: College ID
      - `phone`: Phone number
      - `cn`: Student ID card number (only for students)
      - `team_id`: Team ID (only for students)
      - `email`: Email (only for teachers)
      - `title`: Title (only for teachers)
  - `POST /api/user/login/`: User login
    - **Parameters**:
      - `username`: Username
      - `password`: Password

### 2. Team Module
- **Function**: Team creation, member invitations, and team management.
- **API Endpoints**:
  - `POST /api/team/create-team/`: Create a team and send invitations (only team leaders can do this)
    - **Parameters**:
      - `name`: Team name
      - `description`: Team description
      - `members`: List of member IDs (student IDs)
  - `POST /api/team/confirm-team/`: Confirm team invitation
    - **Parameters**:
      - `team_id`: Team ID
      - `student_id`: Student ID
  - `POST /api/team/invite-new-member/`: Invite a new member (only team leaders can do this)
    - **Parameters**:
      - `team_id`: Team ID
      - `student_id`: Student ID
  - `POST /api/team/invite-new-teacher/`: Invite a new teacher (only team leaders can do this)
    - **Parameters**:
      - `team_id`: Team ID
      - `teacher_id`: Teacher ID
  - `GET /api/team/myteam/`: View my team
  - `GET /api/team/allteam/`: View all teams
  - `DELETE /api/team/dismiss/<int:pk>/`: Dissolve a team (only team leaders can do this)
    - **Parameters**:
      - `pk`: Team ID
  - `PUT /api/team/update/<int:pk>/`: Update team information (only team leaders can do this)
    - **Parameters**:
      - `pk`: Team ID
      - `name`: Team name
      - `description`: Team description
  - `PUT /api/team/quit/<int:pk>/`: Quit the team
    - **Parameters**:
      - `pk`: Team ID

### 3. Competition Module
- **Function**: Competition creation, updating competition information, and competition deletion.
- **API Endpoints**:
  - `POST /api/competition/`: Create a competition (only team leaders can do this)
    - **Parameters**:
      - `title`: Competition title
      - `date`: Competition date
      - `description`: Competition description
      - `score`: Competition score
      - `teacher_num`: Number of teachers
      - `team_id`: Team ID
      - `file`: Certificate image
  - `PUT /api/competition/<int:pk>/`: Update competition information (only team leaders can do this)
    - **Parameters**:
      - `pk`: Competition ID
      - `title`: Competition title
      - `date`: Competition date
      - `description`: Competition description
      - `score`: Competition score
      - `teacher_num`: Number of teachers
      - `file`: Certificate image
  - `DELETE /api/competition/<int:pk>/`: Delete a competition (only team leaders can do this)
    - **Parameters**:
      - `pk`: Competition ID
  - `PUT /api/competition/confirm/<int:pk>/`: Confirm competition information
    - **Parameters**:
      - `pk`: Competition ID
  - `GET /api/competition/my_competitions/`: View my competitions

### 4. College Module
- **Function**: College information management.
- **API Endpoint**:
  - `GET /api/college/`: Get a list of colleges.

### 5. Teacher Module
- **Function**: Teacher information management.
- **API Endpoint**:
  - `GET /api/teacher/info/`: Teacher information CRUD operations
    - **Parameters**:
      - `id`: Teacher ID
      - `name`: Teacher name
      - `email`: Teacher email
      - `title`: Teacher title

### 6. Student Module
- **Function**: Student information management.
- **API Endpoint**:
  - `GET /api/student/info/`: Student information CRUD operations
    - **Parameters**:
      - `id`: Student ID
      - `name`: Student name
      - `cn`: Student ID card number
      - `team_id`: Student team ID
  - `POST /api/student/update_avatar/`: Update student avatar
    - **Parameters**:
      - `avatar`: Avatar image file (JPEG/PNG, max size 5MB)

### 7. Utility Module
- **Function**: Provides common utility functions for the system.
- **Utility Classes**:
  - `minio_utils.py`: Provides utility functions for interacting with the MinIO storage service, including file upload, deletion, and validation.
    - `upload_competition_image_to_minio`: Upload competition images to MinIO and return the URL list.
    - `delete_files_from_minio`: Delete files from MinIO.
    - `validate_image_file`: Validate image file formats and sizes.
  - `token_utils.py`: Provides utility functions for working with JWT tokens.
    - `generate_token`: Generate a JWT token with custom information such as roles.
  - `token_auth_middleware.py`: Provides token-based authentication middleware.
    - `TokenAuthMiddleware`: Middleware to validate the token in requests, ensuring the user is logged in.
  - `csrf_middleware.py`: Provides CSRF token-related middleware.
    - `NotUseCsrfTokenMiddlewareMixin`: Middleware to disable CSRF token validation.
  - `baseView.py`: Provides base view classes.
    - `BaseModelViewSet`: Provides a base ModelViewSet with common exception handling and response formatting.

## 4. Usage Documentation

### Environment Setup
1. Install Python 3.11 or higher.
2. Install required dependencies: `pip install -r requirements.txt`.
3. Configure the environment: Follow the `.env.py` template and create your own `.env` file.
4. Run database migrations: `python manage.py migrate`.
5. Start the development server: `python manage.py runserver 127.0.0.1:8105`.
