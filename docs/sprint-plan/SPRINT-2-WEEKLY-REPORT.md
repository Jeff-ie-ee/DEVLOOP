# DEVLOOP – SPRINT 2 WEEKLY REPORT

**Project Title:** Developer Engineering & Intelligence Platform (DEVLOOP)
**Project Tagline:** Learn. Research. Build. Evolve.
**Sprint:** Sprint 2 – Identity and Access Management
**Planned Duration:** 7 Working Days
**Reporting Date:** 20 November 2026
**Development Methodology:** Agile – Scrum
**Sprint Status:** IN PROGRESS

---

# 1. INTRODUCTION

Sprint 2 focuses on developing a secure and structured Identity and Access Management (IAM) system for the DEVLOOP platform.

The primary goal is to establish a reliable authentication and authorization framework that enables developers to register, log in, access their accounts and interact with platform resources according to their assigned roles.

The sprint introduces secure password management, JSON Web Token (JWT) authentication, authenticated-user identification and Role-Based Access Control (RBAC).

These functionalities provide the security foundation for subsequent DEVLOOP modules, including the coding workspace, project management, code execution and developer analytics.

# 2. SPRINT OBJECTIVES

The major objectives of Sprint 2 are:

1. Implement secure developer registration.
2. Establish password hashing and verification mechanisms.
3. Implement username- and email-based authentication.
4. Introduce JWT-based access-token management.
5. Develop authenticated-user identification.
6. Implement reusable authentication dependencies.
7. Establish developer and administrator roles.
8. Implement Role-Based Access Control.
9. Protect administrative API endpoints.
10. Validate authentication and authorization through automated and live integration testing.

# 3. WORK COMPLETED

## 3.1 Authentication Foundation

- Reviewed the existing User, Role and UserRole database models.
- Established authentication-related dependencies.
- Configured JWT authentication settings.
- Configured a secure JWT signing secret through environment variables.
- Selected HS256 as the JWT signing algorithm.
- Configured a 30-minute access-token lifetime.
- Organized authentication functionality into separate API, schema, service, repository and security layers.

## 3.2 Password Security

Implemented password security functionality using Argon2id.

Work completed:

- Integrated the pwdlib password-hashing library.
- Implemented password hashing.
- Implemented password verification.
- Generated unique salts for password hashes.
- Ensured that plaintext passwords are not stored in the database.
- Tested successful and unsuccessful password verification.

## 3.3 User Registration

**API Endpoint:** `POST /auth/register`

Implemented functionality:

- Developer account creation.
- Username validation.
- Email validation using Pydantic EmailStr.
- Email normalization.
- Password length validation.
- Duplicate username prevention.
- Duplicate email prevention.
- Argon2id password hashing.
- Automatic assignment of the default developer role.
- Database transaction handling.
- Transaction rollback on registration failure.
- Safe user responses without exposing password hashes.

## 3.4 Default Developer Role Management

Implemented the default developer-role provisioning mechanism.

Work completed:

- Created an Alembic migration for the default developer role.
- Provisioned the developer role in PostgreSQL.
- Integrated automatic developer-role assignment during registration.
- Verified the UserRole association.
- Preserved existing database records.

**Migration:** `4a51514eb718`

## 3.5 User Login and Authentication

**API Endpoint:** `POST /auth/login`

Implemented functionality:

- Username-based authentication.
- Email-based authentication.
- Argon2 password verification.
- Invalid credential rejection.
- Unknown-user rejection.
- Inactive-account rejection.
- JWT access-token generation.
- Token signature verification.
- Token expiration validation.
- Bearer token response formatting.

Successful authentication returns a signed access token to the client.

## 3.6 JWT Access Token Implementation

Integrated PyJWT for JSON Web Token generation and verification.

The JWT contains the following claims:

| Claim | Description |
|---|---|
| `sub` | Unique database user identifier |
| `iat` | Token issue time |
| `exp` | Token expiration time |

**JWT Configuration:**

| Parameter | Configuration |
|---|---|
| Signing Algorithm | HS256 |
| Access Token Lifetime | 30 minutes |
| Signing Secret | Environment-based configuration |
| Token Generation | PyJWT |
| Token Validation | Signature and expiration verification |
| Authentication Scheme | Bearer |

## 3.7 Authenticated User Identity

Implemented a reusable JWT Bearer authentication dependency.

Work completed:

- Implemented HTTP Authorization header extraction.
- Implemented JWT signature and expiration validation.
- Extracted the user identifier from the JWT subject claim.
- Implemented authenticated-user retrieval from PostgreSQL.
- Added active-account verification for protected requests.
- Implemented the `GET /auth/me` endpoint.
- Returned authenticated user profile information without exposing password hashes.
- Rejected missing, malformed, invalid and expired tokens.
- Rejected tokens referencing nonexistent or inactive accounts.

**API Endpoint:** `GET /auth/me`

**Integration Result:** Successfully retrieved the registered developer's profile through the live PostgreSQL-backed API using JWT authentication.

## 3.8 Role-Based Access Control (RBAC)

Implemented a reusable role-based authorization mechanism.

Work completed:

- Developed database-backed role verification.
- Implemented the `user_has_role()` repository function.
- Implemented the reusable `require_role()` authorization dependency.
- Established developer and administrator roles.
- Implemented role-based access restrictions.
- Distinguished authentication failures from authorization failures.
- Restricted administrative operations to users assigned the administrator role.

The system distinguishes:

| HTTP Status | Purpose |
|---|---|
| 401 Unauthorized | Missing or invalid authentication |
| 403 Forbidden | Authenticated user without required permission |

## 3.9 Administrator Role Provisioning

Created an Alembic migration to provision the default administrator role.

**Migration ID:** `375938ef2d2a`

**Migration Name:** Seed Default Admin Role

Successfully provisioned the following PostgreSQL roles:

| Role ID | Role Name | Description |
|---|---|---|
| 1 | developer | Standard DEVLOOP developer |
| 2 | admin | DEVLOOP platform administrator |

The migration preserves the existing developer role and user records.

The migration was successfully applied using:

`python -m alembic upgrade head`

Verified migration status:

`375938ef2d2a (head)`

## 3.10 Administrator Account Provisioning

Developed a separate administrator-provisioning script:

`backend/scripts/create_admin.py`

Implemented functionality:

- Secure administrator account creation.
- Private password collection through terminal input.
- Argon2 password hashing.
- Administrator-role assignment.
- Duplicate username and email checks.
- Database transaction management.
- Transaction rollback on failure.
- Database error diagnostics.

Successfully created the first administrator account.

| Attribute | Value |
|---|---|
| User ID | 2 |
| Username | devloop_admin |
| Role | admin |
| Account Status | Active |
| Password Storage | Argon2 hash |

Public registration continues to assign only the developer role. Administrator privileges cannot be obtained through the public registration workflow.

## 3.11 Administrator User Management API

Implemented the administrator-only endpoint:

**GET /admin/users**

Functionality includes:

- Retrieval of registered DEVLOOP users.
- Administrator-only access.
- Database-backed authorization.
- Pagination support.
- Configurable page size.
- Safe user-profile responses.
- Prevention of password-hash exposure.

Pagination parameters:

| Parameter | Default | Validation |
|---|---:|---|
| page | 1 | Minimum 1 |
| page_size | 20 | Between 1 and 100 |

The endpoint uses the UserRead response schema to prevent sensitive password information from being returned.

# 4. TECHNOLOGY STACK

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | FastAPI |
| Database | PostgreSQL 17 |
| ORM | SQLAlchemy |
| Database Migration | Alembic |
| Password Hashing | Argon2id |
| Password Utility | pwdlib |
| Authentication | JSON Web Token (JWT) |
| JWT Library | PyJWT |
| Data Validation | Pydantic |
| Email Validation | email-validator |
| Automated Testing | Pytest |
| API Testing | FastAPI TestClient |
| Code Quality | Ruff |
| Containerization | Docker |
| Version Control | Git and GitHub |
| Frontend Framework | React |
| Frontend Development Server | Vite |

# 5. DATABASE COMPONENTS

The identity and access-management implementation uses the following database tables:

| Table | Purpose |
|---|---|
| `users` | Stores developer accounts, identity information and password hashes |
| `roles` | Stores available platform roles |
| `user_roles` | Maintains user-to-role assignments |

### Database Migration History

| Migration ID | Purpose |
|---|---|
| `4a51514eb718` | Provision default developer role |
| `375938ef2d2a` | Provision default administrator role |

### Current Database Roles

| Role | Purpose |
|---|---|
| developer | Standard developer access |
| admin | Administrative access |

Database interactions are managed through SQLAlchemy, and database schema changes are maintained through Alembic migrations.

# 6. API ENDPOINTS IMPLEMENTED

| Method | Endpoint | Functionality |
|---|---|---|
| GET | `/` | API root information |
| GET | `/health` | Backend health check |
| GET | `/health/database` | Database connectivity check |
| POST | `/auth/register` | Register a new developer |
| POST | `/auth/login` | Authenticate a registered user |
| GET | `/auth/me` | Retrieve authenticated user profile |
| GET | `/admin/users` | Retrieve registered users (admin only) |

# 7. BACKEND ARCHITECTURE

Sprint 2 follows a modular backend architecture with clear separation of responsibilities.

| Layer | Responsibility |
|---|---|
| API Layer | Handles authentication and administration HTTP requests |
| Schema Layer | Validates request and response data |
| Service Layer | Implements registration and authentication business logic |
| Repository Layer | Handles database queries and role operations |
| Security Layer | Handles password hashing and JWT operations |
| Dependency Layer | Provides reusable authentication and authorization checks |
| Database Layer | Manages PostgreSQL connections and SQLAlchemy sessions |

### Authentication Workflow

1. Developer submits registration or login information.
2. FastAPI validates the incoming request.
3. The service layer performs the required operation.
4. The repository layer interacts with PostgreSQL.
5. Argon2 verifies or hashes passwords.
6. A signed JWT is generated after successful authentication.
7. Authenticated-user dependencies validate the token.
8. The corresponding user is retrieved from PostgreSQL.
9. The API returns the appropriate response.

### Authorization Workflow

1. A user sends a request to a protected API endpoint.
2. FastAPI extracts the Bearer token.
3. The JWT is validated.
4. The user is retrieved from PostgreSQL.
5. The user's assigned roles are checked.
6. The requested operation is permitted or rejected.
7. Unauthorized users receive HTTP 401 or HTTP 403, as appropriate.

# 8. TESTING AND VALIDATION

Automated testing has been conducted using Pytest and FastAPI TestClient.

Isolated SQLite databases were used for the registration, authentication, identity and RBAC automated integration tests.

## 8.1 Authentication Tests

| Test Case | Result |
|---|---|
| Username-based login | Passed |
| Email-based login | Passed |
| Incorrect password rejection | Passed |
| Unknown user rejection | Passed |
| Inactive account rejection | Passed |
| Expired JWT rejection | Passed |

**Result: 6/6 Passed**

## 8.2 Registration Tests

| Test Case | Result |
|---|---|
| Successful registration | Passed |
| Duplicate email rejection | Passed |
| Duplicate username rejection | Passed |
| Invalid email rejection | Passed |
| Short password rejection | Passed |
| Automatic developer-role assignment | Passed |

**Result: 6/6 Passed**

## 8.3 Current-User Identity Tests

| Test Case | Result |
|---|---|
| Valid JWT profile retrieval | Passed |
| Missing token rejection | Passed |
| Invalid token rejection | Passed |
| Expired token rejection | Passed |
| Unknown user rejection | Passed |
| Inactive user rejection | Passed |

**Result: 6/6 Passed**

## 8.4 Password Security Tests

| Test Case | Result |
|---|---|
| Password hashing | Passed |
| Correct password verification | Passed |
| Incorrect password rejection | Passed |
| Unique salt generation | Passed |

**Result: 4/4 Passed**

## 8.5 Existing API Tests

| Test Case | Result |
|---|---|
| Root endpoint testing | Passed |
| Backend health endpoint testing | Passed |

**Result: 2/2 Passed**

## 8.6 Role-Based Access Control Tests

| Test Case | Result |
|---|---|
| Administrator can list registered users | Passed |
| Developer cannot access admin endpoint | Passed |
| Missing authentication token rejected | Passed |
| Inactive administrator rejected | Passed |
| Public registration cannot assign admin role | Passed |

**Result: 5/5 Passed**

## 8.7 Overall Backend Testing Results

| Test Category | Tests Passed |
|---|---:|
| Authentication | 6 |
| Registration | 6 |
| Current-User Identity | 6 |
| Password Security | 4 |
| Existing API | 2 |
| Role-Based Access Control | 5 |
| **TOTAL** | **29/29** |

**Overall Result: All 29 automated backend tests passed.**

## 8.8 Live RBAC Integration Testing

Administrator and developer authorization were successfully verified against the live PostgreSQL database.

| Test Scenario | Expected Result | Actual Result |
|---|---|---|
| Administrator login | 200 OK | Passed |
| Administrator accesses `GET /admin/users` | 200 OK | Passed |
| Developer accesses `GET /admin/users` | 403 Forbidden | Passed |
| Inactive administrator access | 401 Unauthorized | Automated test passed |
| Unauthenticated admin request | 401 Unauthorized | Automated test passed |

### Verified Administrator Response

The administrator successfully retrieved the registered user profiles:

- `devloop_test_01` – Developer
- `devloop_admin` – Administrator

The response did not expose password hashes.

### Verified Developer Restriction

The developer account received:

**HTTP 403 Forbidden**

Response:

```json
{
  "detail": "You do not have permission to access this resource."
}
```

This confirms that ordinary developer accounts cannot access administrator-only resources.

## 8.9 Code Quality and Dependency Validation

- Ruff validation: All checks passed.
- Dependency validation: No broken requirements found.
- JWT generation and verification: Passed.
- Expired-token rejection: Passed.
- Password hashing validation: Passed.
- Database migration validation: Passed.
- Live PostgreSQL administrator access: Passed.
- Live PostgreSQL developer restriction: Passed.

# 9. SECURITY MEASURES IMPLEMENTED

The following security measures have been implemented:

1. Argon2id password hashing.
2. Unique salts for password hashes.
3. JWT signature verification.
4. Access-token expiration validation.
5. Environment-based JWT signing secret.
6. Generic authentication error messages.
7. Inactive-account login restriction.
8. Duplicate account prevention.
9. Automatic default developer-role assignment.
10. Restricted administrator provisioning.
11. Reusable JWT Bearer authentication dependencies.
12. Database-backed role verification.
13. Administrator-only endpoint protection.
14. HTTP 401 and HTTP 403 authorization handling.
15. Database transaction rollback on registration and provisioning failures.
16. Protection against password-hash exposure in API responses.
17. Protection against public administrator-role assignment.

# 10. VERSION CONTROL AND PROJECT MANAGEMENT

The DEVLOOP project is maintained using Git and GitHub.

**GitHub Repository:**
https://github.com/Jeff-ie-ee/DEVLOOP

### Previously Published Commits

| Commit | Description |
|---|---|
| `2799c32` | Complete Sprint 1 engineering foundation |
| `53d15c1` | Add Sprint 1 weekly report |
| `8eec2ca` | Implement secure user registration |
| `18efb1a` | Implement JWT login authentication |
| `1d50e0e` | Implement authenticated user identity |
| `7382218` | Update Sprint 2 progress report |

The current RBAC implementation, administrator-role migration, provisioning script, administration API and RBAC tests have passed local validation. These changes are pending their GitHub commit and push.

# 11. REMAINING SPRINT WORK

The following functionalities remain planned for completion.

## 11.1 Session Management

- Implement refresh-token generation.
- Implement secure refresh-token storage.
- Implement refresh-token rotation.
- Implement token revocation.
- Implement secure logout functionality.
- Validate session expiration and token reuse behaviour.

## 11.2 Protected Developer APIs

- Integrate authentication dependencies into additional workspace endpoints.
- Protect developer-specific resources.
- Restrict access to user-owned projects.
- Validate unauthorized resource access.

## 11.3 Frontend Authentication

- Develop the React login interface.
- Develop the registration interface.
- Integrate authentication APIs with React.
- Implement authentication state management.
- Implement protected workspace navigation.
- Integrate logout functionality.

## 11.4 Frontend Role Management

- Integrate developer and administrator roles into the frontend.
- Implement role-aware navigation.
- Restrict administrative interface access.
- Connect administrative interfaces to protected backend APIs.

## 11.5 Final Integration and Validation

- Conduct backend and frontend integration testing.
- Validate registration, authentication and authorization workflows.
- Test session-management functionality.
- Complete security validation.
- Run the complete automated backend test suite.
- Perform final code-quality and dependency checks.
- Update technical documentation.
- Complete the Sprint 2 review.
- Synchronize the final Sprint 2 implementation with GitHub.

# 12. SPRINT OUTCOME

Sprint 2 has successfully established the core Identity and Access Management infrastructure for DEVLOOP.

The implementation now supports secure developer registration, Argon2id password hashing, username- and email-based authentication, JWT access-token generation, authenticated-user identification and database-backed Role-Based Access Control.

Two principal platform roles, developer and administrator, have been provisioned.

The administrator can retrieve registered user profiles through the protected administration endpoint, while ordinary developers are prevented from accessing administrator-only resources.

The completed implementation has been validated through 29 automated backend tests, all of which passed.

Live integration testing against PostgreSQL also confirmed successful administrator access and developer authorization restrictions.

The completed work provides the security foundation for the forthcoming session-management, frontend authentication and protected developer workspace capabilities.

# 13. CONCLUSION

Sprint 2 has made substantial progress towards establishing a secure and structured Identity and Access Management system for DEVLOOP.

The registration, authentication, identity verification and authorization functionalities provide the foundation for identifying developers and controlling access to platform resources.

The backend now supports separate developer and administrator roles, protected administrative operations and verified access restrictions.

The next development stage will focus on refresh-token management, secure logout, frontend authentication and broader protected API integration.

**Sprint 2 Status: IN PROGRESS**

---

**Project:** DEVLOOP
**Project Tagline:** Learn. Research. Build. Evolve.
