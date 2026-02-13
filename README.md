MO-IT152 - Integrative Programming and Technologies (A3101)
Group 11 - Connectly API (Security + Design Patterns + Likes/Comments)

Members
- Charmaine Nabor
- Emmar Alvarez
- Christian Paul Penaflor
- Kenneth Ian Lu

Project Overview
Connectly is a Django REST Framework (DRF) API that supports:
- User registration
- Posts CRUD
- Comments CRUD
- Likes and comments on posts (Homework feature)
- Token Authentication
- HTTPS testing (self-signed certificate for local testing)
- Ownership-based access control (only the author can update/delete)
- Design Patterns: **Singleton** (Logger/Config) and **Factory** (Post creation)

Features Implemented

1) Security Enhancements
- HTTPS (local testing only) using a self-signed certificate
- Token Authentication using DRF authtoken
- Password Hashing (stored securely in `auth_user`, not plain text)
- Ownership / Permissions
  - Only the post author can update/delete their post
  - Only the comment author can delete their comment
- Logging (security + request logs via Singleton logger)

2) Design Patterns
- Singleton Pattern
  - Centralized logger so the whole API shares the same logger instance
  - Optional config manager for shared settings

- Factory Pattern
  - Centralized object creation logic for posts
  - Makes it easier to validate and extend post creation later (new post types)

Setup Instructions

1) Create and activate virtual environment
Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
