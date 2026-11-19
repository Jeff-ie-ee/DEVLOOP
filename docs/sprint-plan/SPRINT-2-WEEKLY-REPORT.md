# DEVLOOP – SPRINT 2 REPORT

**Project Title:** Developer Engineering & Intelligence Platform (DEVLOOP)
**Sprint:** Sprint 2 – Identity and Access Management
**Duration:** 7 Working Days
**Reporting Date:** 19 November 2026
**Sprint Status:** In Progress
**Development Methodology:** Agile – Scrum

---

## 1. Sprint Objective

The primary objective of Sprint 2 is to implement a secure Identity and Access Management (IAM) system for the DEVLOOP platform.

The sprint focuses on establishing user registration, authentication, JWT-based access management, authenticated-user identification and Role-Based Access Control (RBAC).

The objective is to ensure that every developer has a secure identity and that access to platform resources can be controlled according to user roles and permissions.

## 2. Work Completed

### 2.1 Authentication Foundation

- Reviewed the existing User, Role and UserRole database models.
- Integrated authentication and security dependencies.
- Configured JWT authentication settings.
- Generated and configured a secure JWT signing secret through environment variables.
- Configured the HS256 signing algorithm.
- Established a default access-token lifetime of 30 minutes.
- Organized authentication functionality into separate API, schema, service, repository and security layers.

### 2.2 Password Security

- Integrated the pwdlib password-hashing library.
- Implemented Argon2id password hashing.
- Developed password verification functionality.
- Implemented unique password salts.
- Ensured that plaintext passwords are not stored in the database.
- Verified correct and incorrect password authentication.

### 2.3 User Registration

Implemented the following API endpoint:

**POST /auth/register**

Functionalities include:

- User account creation.
- Username validation.
- Email validation using Pydantic EmailStr.
- Email normalization.
- Password length validation.
- Duplicate username prevention.
- Duplicate email prevention.
- Argon2 password hashing.
- Automatic assignment of the default developer role.
- Database transaction handling and rollback.
- Safe API responses without exposing password hashes.

### 2.4 Default Role Management

- Created an Alembic migration for the default developer role.
- Provisioned the developer role in PostgreSQL.
- Implemented automatic role assignment during user registration.
- Verified the UserRole association in the database.
- Preserved the existing identity database schema.

**Migration ID:** `4a51514eb718`

### 2.5 User Login and Authentication

Implemented the following API endpoint:

**POST /auth/login**

Functionalities include:

- Username-based authentication.
- Email-based authentication.
- Argon2 password verification.
- Invalid credential rejection.
- Unknown user rejection.
- Inactive account rejection.
- JWT access-token generation.
- Token signature verification.
- Token expiration validation.
- Bearer token response formatting.

### 2.6 JWT Access Token Implementation

Implemented signed JSON Web Tokens using PyJWT.

The token contains:

| Claim | Purpose |
|---|---|
| `sub` | Unique user identifier |
| `iat` | Token issue time |
| `exp` | Token expiration time |

Authentication configuration:

- Algorithm: HS256
- Token lifetime: 30 minutes
- Signing secret: Environment-based configuration
- Token validation: Signature and expiration verification

### 2.7 Authenticated User Identity

Implemented a reusable authentication dependency and the authenticated-user profile endpoint.

Functionalities include:

- Implemented a reusable JWT Bearer authentication dependency.
- Integrated HTTP Authorization header extraction.
- Implemented JWT signature and expiration validation.
- Extracted the user identifier from the JWT subject claim.
- Implemented authenticated-user retrieval from PostgreSQL.
- Added active-account verification for protected requests.
- Implemented the `GET /auth/me` endpoint.
- Returned authenticated user profile information without exposing password hashes.
- Rejected missing, malformed, invalid and expired tokens.
- Rejected tokens referencing nonexistent or inactive accounts.

**Integration Result:** Successfully retrieved the registered developer's profile through the live PostgreSQL-backed API using JWT authentication.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migration Tool | Alembic |
| Password Hashing | Argon2id |
| Password Utility | pwdlib |
| Authentication | JWT |
| JWT Library | PyJWT |
| Validation | Pydantic |
| Email Validation | email-validator |
| Automated Testing | Pytest |
| API Testing | FastAPI TestClient |
| Code Quality | Ruff |
| Containerization | Docker |
| Version Control | Git and GitHub |

## 4. Database Components

The following identity-related database tables are established:

| Table | Purpose |
|---|---|
| `users` | Stores user identity and password hashes |
| `roles` | Stores platform roles |
| `user_roles` | Maps users to assigned roles |

The default `developer` role has been provisioned through an Alembic migration.

Database operations are managed using SQLAlchemy, while schema versioning is maintained through Alembic.

## 5. API Endpoints Implemented

| Method | Endpoint | Functionality |
|---|---|---|
| GET | `/` | API root information |
| GET | `/health` | Backend health check |
| GET | `/health/database` | Database connectivity check |
| POST | `/auth/register` | Register a new developer |
| POST | `/auth/login` | Authenticate a registered user |
| GET | `/auth/me` | Retrieve authenticated user profile |

## 6. Backend Architecture

Sprint 2 follows a modular backend architecture with separated responsibilities.

| Layer | Responsibility |
|---|---|
| API Layer | Handles authentication HTTP requests and responses |
| Schema Layer | Validates registration, login and response data |
| Service Layer | Implements registration and authentication business logic |
| Repository Layer | Performs user, role and database operations |
| Security Layer | Handles Argon2 password hashing and JWT operations |
| Database Layer | Manages PostgreSQL connections and SQLAlchemy sessions |

### Authentication Request Workflow

1. The developer submits registration or login information.
2. FastAPI validates the incoming request.
3. The service layer performs the authentication or registration operation.
4. The repository layer interacts with PostgreSQL.
5. Passwords are processed using Argon2id.
6. JWT tokens are generated and verified through the security layer.
7. Authenticated-user dependencies identify the corresponding database user.
8. The API returns the appropriate response.

## 7. Testing and Validation

Automated testing has been conducted using Pytest with isolated SQLite databases for registration, authentication and current-user integration tests.

### 7.1 Authentication Tests

| Test Case | Result |
|---|---|
| Username-based login | Passed |
| Email-based login | Passed |
| Incorrect password rejection | Passed |
| Unknown user rejection | Passed |
| Inactive account rejection | Passed |
| Expired JWT rejection | Passed |

### 7.2 Registration Tests

| Test Case | Result |
|---|---|
| Successful registration | Passed |
| Duplicate email rejection | Passed |
| Duplicate username rejection | Passed |
| Invalid email rejection | Passed |
| Short password rejection | Passed |
| Automatic developer-role assignment | Passed |

### 7.3 Current-User Identity Tests

| Test Case | Result |
|---|---|
| Valid JWT profile retrieval | Passed |
| Missing token rejection | Passed |
| Invalid token rejection | Passed |
| Expired token rejection | Passed |
| Unknown user rejection | Passed |
| Inactive user rejection | Passed |

### 7.4 Password Security Tests

| Test Case | Result |
|---|---|
| Password hashing | Passed |
| Correct password verification | Passed |
| Incorrect password rejection | Passed |
| Unique salt generation | Passed |

### 7.5 Existing API Tests

- Root endpoint testing.
- Backend health endpoint testing.

### 7.6 Overall Backend Test Results

| Test Category | Tests Passed |
|---|---:|
| Authentication | 6 |
| Registration | 6 |
| Current-User Identity | 6 |
| Password Security | 4 |
| Existing API | 2 |
| **Total** | **24/24** |

**Overall Result:** All 24 automated backend tests passed.

### 7.7 Code Quality and Dependency Validation

- Ruff validation: All checks passed for the targeted application, test and migration files.
- Dependency validation: No broken requirements found.
- JWT generation: Passed.
- JWT signature verification: Passed.
- JWT expiration verification: Passed.
- Inactive-account protection: Passed.
- Live PostgreSQL user-profile integration: Passed.

## 8. Security Measures Implemented

The following security measures have been implemented:

1. Argon2id password hashing.
2. Unique salts for password hashes.
3. JWT signature verification.
4. Token expiration validation.
5. Generic authentication error messages.
6. Inactive-account login restriction.
7. Duplicate account prevention.
8. Environment-based JWT signing secret.
9. Restricted default developer-role assignment.
10. Database transaction rollback on registration failure.
11. Bearer token authentication.
12. Authenticated-user verification through database lookup.
13. Rejection of invalid and expired access tokens.
14. Protection of user profile responses from password-hash exposure.

## 9. Version Control and Project Management

The DEVLOOP project is maintained using Git and GitHub.

**Repository:** Jeff-ie-ee/DEVLOOP

**GitHub:** https://github.com/Jeff-ie-ee/DEVLOOP

The following commits have been published:

| Commit | Description |
|---|---|
| `2799c32` | Complete Sprint 1 engineering foundation |
| `53d15c1` | Add Sprint 1 weekly report |
| `8eec2ca` | Implement secure user registration |
| `18efb1a` | Implement JWT login authentication |

The authenticated-user identity implementation has also been committed locally and is pending its GitHub push.

## 10. Remaining Sprint Work

The following functionalities remain to be implemented or validated:

### 10.1 Protected API Access

- Integrate JWT authentication dependencies into selected API routes.
- Protect developer workspace resources.
- Reject unauthorized requests.
- Validate access using Bearer tokens.

### 10.2 Role-Based Access Control

- Define platform roles and permissions.
- Implement role-checking dependencies.
- Restrict administrative operations.
- Validate developer and administrator permissions.

### 10.3 Session Management

- Implement refresh-token functionality.
- Implement token revocation and session management.
- Integrate secure logout behaviour.

### 10.4 Frontend Authentication

- Develop login and registration interfaces.
- Integrate authentication APIs with React.
- Implement authentication state management.
- Add protected workspace navigation.
- Integrate logout functionality.

### 10.5 Final Integration

- Conduct backend and frontend integration testing.
- Validate authorization workflows.
- Complete automated security testing.
- Update technical documentation.
- Complete the Sprint 2 review and final GitHub synchronization.

## 11. Sprint Outcome

Sprint 2 has successfully established the core identity registration, login authentication and authenticated-user identification functionality of DEVLOOP.

The system supports secure account registration, Argon2id password hashing, username/email authentication, JWT access-token generation, active-account verification and authenticated-user profile retrieval.

The backend now includes three principal authentication endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

The implementation has been validated through 24 automated backend tests, with all tests passing.

The completed work establishes a foundation for protected API access, role-based authorization and frontend authentication integration.

## 12. Conclusion

Sprint 2 has made significant progress towards establishing a secure and structured Identity and Access Management system for DEVLOOP.

The registration, login and authenticated-user identity functionalities provide the foundation for identifying developers and controlling access to platform resources.

The next development stage will focus on protected API endpoints, role-based authorization, session management and frontend integration.

**Sprint 2 Status: IN PROGRESS**

---

**Project:** DEVLOOP
**Tagline:** Learn. Research. Build. Evolve.
