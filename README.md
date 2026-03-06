**MO-IT152 - Integrative Programming and Technologies (A3101)**

**Group 11 - Connectly API (+ Likes/Comments + Newsfeed + Google Oauth Login)**

**Members:**
- Charmaine Nabor
- Emmar Alvarez
- Christian Paul Penaflor
- Kenneth Ian Lu

**Project Overview**

Connectly is a Django REST Framework (DRF) API designed to provide a secure and extensible backend for social interaction applications. It integrates advanced security measures, ownership-based access control, social login, and modern design patterns to maintain code quality and reusability.

The API supports:
1. User registration and management
   - Users register with unique email addresses
   - Passwords are securely hashed using Argon2 / PBKDF2 / BCrypt
   - Users can log in via token authentication (DRF token & JWT) or Google OAuth2
2. Posts CRUD (Create, Read, Update, Delete)
   - Authenticated users can create, edit, and delete posts
   - Post types include text, image, and video
   - Image posts require metadata file_size; video posts require duration
   - Posts are created via a Factory Pattern to centralize validation and future extensibility
3. Likes on posts
   - Authenticated users can like posts
   - Duplicate likes are prevented using a database-level uniqueness constraint
4. Comments on posts
   - Users can comment on posts
   - Only the comment author can delete their comment
   - Comments are linked to both the user and the post
5. Newsfeed with pagination and filtering
   - Posts are returned sorted by newest first
   - Pagination is applied (default page size: 5)
   - Optional filtering: display only posts liked by the logged-in user
6. Ownership-based permissions
   - Only post authors can update/delete their posts
   - Only comment authors can delete their comments
7. Login via Google OAuth2
   - Users can authenticate with Google
   - New users are automatically created if not existing
   - JWT tokens are issued for authenticated sessions
8. Security Enhancements
   - HTTPS supported for local testing with self-signed certificates
   - Token-based authentication ensures secure API access
   - Passwords are never stored in plain text
   - Logs capture critical security and request events
9. Logging and Monitoring
   - Centralized Singleton Logger logs all user activity and system events
   - Helps monitor post creation, likes, comments, and errors
10. Design Patterns
   - Singleton Pattern: Logger and optional configuration manager
   - Factory Pattern: Post creation logic centralized for validation and extensibility

**Project Structure**
connectly_project/
├─ authentication/
│ ├─ models.py # CustomUser model
│ ├─ views.py # Google OAuth login
│ ├─ urls.py # Authentication endpoints
├─ posts/
│ ├─ models.py # Post, Comment, Like
│ ├─ views.py # CRUD operations, likes, comments, newsfeed
│ ├─ serializers.py # DRF serializers for Post, Comment, Like
│ ├─ permissions.py # Ownership-based permissions
│ ├─ urls.py # Post and comment endpoints
│ ├─ singletons/
│ │ ├─ logger_singleton.py # Singleton Logger
│ │ ├─ config_singleton.py # Optional Config Manager
│ ├─ factories/
│ │ ├─ post_factory.py # Factory Pattern for Post creation
├─ settings.py # Project configuration and DRF settings
├─ urls.py # Root URL configuration

**API Endpoints**
1. Users
   - GET /api/users/ - List all users
   - POST /api/users/ - Create a new user
2. Authentication
   - POST /api/token/ - Obtain auth token
   - POST /api/token/refresh/ - Refresh JWT token
   - POST /api/auth/google/login/ - Google OAuth login
3. Posts
   - GET /api/posts/ - List all posts
   - POST /api/posts/ - Create a new post
   - GET /api/posts/<id>/ - Retrieve a single post
   - PUT /api/posts/<id>/ - Update a post (author only)
   - DELETE /api/posts/<id>/ - Delete a post (author only)
   - POST /api/posts/<id>/like/ - Like a post
   - POST /api/posts/<id>/comment/ - Comment on a post
   - GET /api/posts/<id>/comments/ - List comments for a post
4. Comments
   - GET /api/comments/ - List all comments
   - POST /api/comments/ - Create a comment (with post ID)
   - DELETE /api/comments/<id>/ - Delete a comment (author only)
5. Newsfeed
   - GET /api/feed/ - Retrieve paginated posts feed
   - Query param liked_only=true - Filter feed to posts liked by the user

**Design & Security Highlights**
1. Factory Pattern for Posts: Ensures all posts are validated consistently before creation.
2. Singleton Logger: Centralizes logging across all views and models.
3. Singleton Config Manager (optional): Centralized app-wide settings.
4. Ownership Permissions: Prevents unauthorized modifications.
5. Token & Social Authentication: Secures API access.
6. Pagination & Filtering: Improves scalability and user experience.

**AI Assistance Disclosure**

AI tools (ChatGPT, Gemini) were used as a supportive resource throughout the development of this project. This included:
   - Generating and refining portions of the codebase.
   - Improving readability through clearer comments, docstrings, and documentation.
   - Suggesting structural improvements and alternative implementations.
   - Providing example patterns, debugging guidance, and explanations of technical concepts.

The project team reviewed, modified, and integrated all AI-assisted code to ensure correctness, security, and alignment with project requirements. All final design and implementation decisions were made by the team.
