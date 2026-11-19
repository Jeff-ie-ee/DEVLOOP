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

The sprint focuses on establishing user registration, authentication, JWT-based access management and Role-Based Access Control (RBAC).

The objective is to ensure that every developer has a secure identity and that access to platform resources can be controlled according to user roles and permissions.

## 2. Work Completed

### 2.1 Authentication Foundation

- Reviewed the existing User, Role and UserRole database models.
- Integrated authentication and security dependencies.
- Configured JWT authentication settings.
- Generated and configured a secure JWT signing secret through environment variables.
- Configured the HS256 signing algorithm.
- Established a default access-token lifetime of 30 minutes.

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

### 2.7 Backend Architecture

Established and expanded the modular backend structure:

- API layer
- Schema layer
- Service layer
- Repository layer
- Security utilities
- Database models
- Database migration management

The implementation separates HTTP handling, data validation, business logic and database operations.

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
| Testing Framework | Pytest |
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

**Migration ID:** `4a51514eb718`

The migration chain is maintained without modifying the original Sprint 1 identity migration.

## 5. API Endpoints Implemented

| Method | Endpoint | Functionality |
|---|---|---|
| POST | `/auth/register` | Register a new developer |
| POST | `/auth/login` | Authenticate a registered user |
| GET | `/` | API root information |
| GET | `/health` | Backend health check |
| GET | `/health/database` | Database connectivity check |

## 6. Testing and Validation

Automated testing has been conducted using Pytest with an isolated SQLite database for registration and authentication integration tests.

### 6.1 Authentication Tests

| Test Case | Result |
|---|---|
| Username-based login | Passed |
| Email-based login | Passed |
| Incorrect password rejection | Passed |
| Unknown user rejection | Passed |
| Inactive account rejection | Passed |
| Expired JWT rejection | Passed |

### 6.2 Registration Tests

| Test Case | Result |
|---|---|
| Successful registration | Passed |
| Duplicate email rejection | Passed |
| Duplicate username rejection | Passed |
| Invalid email rejection | Passed |
| Short password rejection | Passed |
| Automatic developer-role assignment | Passed |

### 6.3 Password Security Tests

| Test Case | Result |
|---|---|
| Password hashing | Passed |
| Correct password verification | Passed |
| Incorrect password rejection | Passed |
| Unique salt generation | Passed |

### 6.4 Existing API Tests

- Root endpoint testing.
- Backend health endpoint testing.

### Overall Backend Test Results

| Test Category | Passed |
|---|---:|
| Authentication | 6 |
| Registration | 6 |
| Password Security | 4 |
| Existing API | 2 |
| **Total** | **18/18** |

### Code Quality Validation

- Targeted Ruff checks: All checks passed.
- Dependency validation: No broken requirements found.
- JWT generation and signature verification: Passed.
- Expired JWT rejection: Passed.

## 7. Security Measures Implemented

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

## 8. Remaining Sprint Work

The following functionalities remain to be implemented or validated:

### 8.1 Authenticated User Identity
- Implement `GET /auth/me`.
- Extract authenticated user identity from JWT.
- Validate user existence and active status.

### 8.2 Protected API Access
- Implement reusable authentication dependencies.
- Protect selected API endpoints.
- Reject requests without valid Bearer tokens.

### 8.3 Role-Based Access Control
- Define platform roles and permissions.
- Implement role-checking dependencies.
- Restrict administrative operations.
- Validate unauthorized access rejection.

### 8.4 Session Management
- Implement refresh-token functionality.
- Implement token revocation and session management.
- Integrate secure logout behaviour.

### 8.5 Frontend Authentication
- Develop login and registration interfaces.
- Integrate authentication APIs with React.
- Implement authentication state management.
- Add protected workspace navigation.
- Integrate logout functionality.

### 8.6 Final Integration
- Conduct backend and frontend integration testing.
- Validate authorization workflows.
- Complete automated security testing.
- Update technical documentation.
- Complete the Sprint 2 review and final GitHub synchronization.

## 9. Version Control and Project Management

The Sprint 1 foundation and Sprint 2 registration implementation have been committed and pushed to GitHub.

**Repository:** Jeff-ie-ee/DEVLOOP

**GitHub:** https://github.com/Jeff-ie-ee/DEVLOOP

Recorded commits:

| Commit | Description |
|---|---|
| `2799c32` | Sprint 1 engineering foundation |
| `53d15c1` | Sprint 1 weekly report |
| `8eec2ca` | Sprint 2 secure user registration |

The login and JWT authentication implementation is undergoing final development validation and has not yet been committed.

## 10. Sprint Outcome

Sprint 2 has successfully established the core identity registration and login functionality of DEVLOOP.

The system now supports secure account registration, Argon2id password hashing, username/email authentication, JWT access-token generation and inactive-account restrictions.

The backend registration and authentication workflows have been validated through 18 automated tests.

The project has established a foundation for implementing protected API access, identity verification and role-based authorization.

## 11. Conclusion

Sprint 2 has made significant progress towards establishing a secure and structured identity management system for DEVLOOP.

The completed registration and authentication functionalities provide the foundation for controlling access to the platform and supporting individual developer accounts.

The remaining work will focus on authenticated-user verification, protected API endpoints, role-based authorization, session management and frontend integration.

**Sprint 2 Status: IN PROGRESS**

---

**Project:** DEVLOOP
**Tagline:** Learn. Research. Build. Evolve.
