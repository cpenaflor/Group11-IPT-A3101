MO-IT152 - Integrative Programming and Technologies (A3101)
Group 11 - Connectly API (Security + Design Patterns)

Members
- Charmaine Nabor
- Emmar Alvarez
- Christian Paul Penaflor
- Kenneth Ian Lu

Project Overview
This project is a Django REST Framework API called Connectly with:
- User registration
- Posts CRUD
- Comments CRUD
- Token Authentication
- HTTPS testing (self-signed cert)
- Role/Object-based access control (RBAC / ownership checks)
- Design Patterns: Singleton (Logger / Config) and Factory (Post creation)

Features Implemented
1) Security Enhancements
- HTTPS (self-signed certificate for local testing)
- Token Authentication** using DRF authtoken
- Password Hashing stored securely in `auth_user` table (no plain text)
- Permissions / Ownership
  - Only the post owner can update/delete their post
  - Only the comment owner can delete their comment

2) Design Patterns
- Singleton Pattern
  - Centralized logger (shared instance) for consistent logs across API
  - Optional config manager for shared settings

- Factory Pattern
  - Centralized post creation logic (future-ready for multiple post types)
  - Keeps object creation consistent and organized

API Endpoints (Main)
Base URL:
- `https://127.0.0.1:8000/api/`

| Method | Endpoint | Description |
|-------|----------|-------------|
| POST | `/users/` | Create user |
| GET | `/users/` | List users |
| POST | `/token/` | Get auth token |
| GET/POST | `/posts/` | List posts / Create post |
| GET/PUT/DELETE | `/posts/<id>/` | Post detail / update / delete |
| GET/POST | `/comments/` | List comments / Create comment |
| DELETE | `/comments/<id>/` | Delete comment |

Testing (Postman)
Steps tested:
1. Create User1 and User2  
2. Generate token for each user  
3. Create post as User1  
4. Try deleting User1 post using User2 token (should be forbidden / denied)  
5. Confirm passwords are hashed in SQLite  
6. Confirm requests work using HTTPS endpoints

Evidence / Deliverables
- GitHub Repository: (PUT LINK HERE)
- Postman Collection Export (JSON): ([https://docs.google.com/spreadsheets/d/1WrKqqyXRkNoaS1sx83kJrv5LhkSg3kMyzXMnbicDqzU/edit?usp=sharing])
- Postman Test Results / Screenshots: ([https://drive.google.com/drive/folders/1gYibSdbx25ILRXgO1UwH5ap_h3-FQdOh?usp=sharing])
- Google Drive Folder (Evidence): ([https://drive.google.com/drive/folders/1gYibSdbx25ILRXgO1UwH5ap_h3-FQdOh?usp=sharing])

Database Verification (SQLite)
Verified tables in DB Browser for SQLite:
- `auth_user` (hashed passwords)
- `posts_post`
- `posts_comment`
- `authtoken_token`

Notes
- HTTPS is for local testing only (self-signed certificate).
- Token authentication is required for protected endpoints like posts/comments.
