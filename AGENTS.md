# AGENTS.md: Guidelines for AI Code Generation Agents

This document provides specific technical guidelines and expectations for AI agents (like Jules) working on the `RealValue` codebase. Its purpose is to ensure consistency, maintainability, and alignment with project architectural principles.

## 1. Project Overview & Architecture

The `RealValue` project is a **monorepo** consisting of:

* **`frontend/`**: Mobile application (React Native, using TypeScript).
* **`backend/`**: RESTful API (Python Flask, using SQLAlchemy for ORM).
* **`shared/`**: Common data models and utility functions used by both frontend and backend.

Agents should understand the clear separation of concerns:
* **Frontend**: User interface, user interactions, local state, and consuming backend APIs.
* **Backend**: Data persistence, business logic, authentication/authorization, and exposing data via RESTful endpoints.
* **Shared**: Source of truth for common data structures (e.g., user profiles, skill definitions) to ensure type and data consistency across the stack.

## 2. Coding Standards & Style

Adherence to established coding standards is paramount for readability and maintainability.

### 2.1 General Principles

* **Readability:** Code must be clean, self-documenting where possible, and easy to understand for human developers.
* **Modularity:** Break down complex logic into smaller, testable functions/modules.
* **DRY (Don't Repeat Yourself):** Avoid redundant code. Utilize shared utilities or abstract common patterns.
* **Explicit over Implicit:** Be clear about intentions. Avoid clever, obscure code.

### 2.2 Frontend (TypeScript/React Native)

* **Linting:** Adhere strictly to the ESLint rules defined in `frontend/.eslintrc.js` (will be configured). Run `npm run lint:fix` before submitting changes.
* **Formatting:** Use Prettier for code formatting. Run `npm run format` (will be configured) regularly.
* **TypeScript:**
    * All new frontend code **must** be written in TypeScript (`.tsx` or `.ts`).
    * Utilize type annotations for function parameters, return values, and complex state/props.
    * Define custom types/interfaces for complex data structures, ideally leveraging types from `shared/` models.
    * Avoid `any` type unless absolutely unavoidable and explicitly justified.
* **React Components:**
    * Prefer functional components with React Hooks.
    * Props should be explicitly typed using TypeScript interfaces.
    * State management: For local component state, use `useState`. For global application state, prefer `React Context API` initially. Avoid Redux unless a clear need for complex, centralized state management arises.
* **Naming Conventions:**
    * Components: PascalCase (e.g., `UserProfileCard.tsx`).
    * Hooks: `use` prefix (e.g., `useAuth.ts`).
    * Functions/Variables: camelCase.
    * Constants: UPPER_SNAKE_CASE (e.g., `MAX_UPLOAD_SIZE`).

### 2.3 Backend (Python Flask)

* **Linting & Formatting:** Use `Black` for code formatting and `Flake8` for linting.
    * Install: `pip install black flake8`
    * Run: `black .` and `flake8 .` before submitting changes.
* **Pythonic Code:** Write idiomatic Python code (PEP 8 compliance).
* **Type Hinting:** Use Python type hints for function parameters, return values, and variable annotations.
* **API Design:**
    * Follow RESTful principles for API endpoints (e.g., `/users`, `/skills`, `/favors`).
    * Use appropriate HTTP methods (GET, POST, PUT, DELETE).
    * Return consistent JSON responses with clear status codes.
* **Database Interactions:**
    * All database interactions should go through `app/models` using Flask-SQLAlchemy ORM. Avoid raw SQL queries unless explicitly necessary and justified.
    * Ensure proper transaction management for data integrity.
* **Naming Conventions:**
    * Classes: PascalCase (e.g., `UserModel`).
    * Functions/Variables: snake_case.
    * Constants: UPPER_SNAKE_CASE.
    * Modules: snake_case (e.g., `main_routes.py`).

### 2.4 Shared Module

* **Consistency:** Models defined in `shared/` should be designed to be convertible to both frontend (TypeScript) and backend (Python) representations.
* **Minimalism:** Only include truly shared definitions. Avoid application-specific logic here.
* **Type Mirroring:** If a Python model is defined, ensure its TypeScript equivalent (or schema) is clear for frontend consumption. (Agents may need to infer or create these type mirrors if not explicitly provided.)

## 3. Testing Guidelines

Robust testing is crucial. Agents are expected to generate and maintain tests for new or modified code.

* **Test Coverage:** Aim for high unit test coverage for all new functions/classes. Integration tests for API endpoints and critical component interactions are also expected.
* **Test Location:**
    * Frontend tests: `frontend/__tests__/` (or similar as per React Native conventions).
    * Backend tests: `backend/tests/`.
* **Test Principles:**
    * **AAA (Arrange-Act-Assert):** Structure tests clearly.
    * **Atomic:** Each test should focus on a single piece of functionality.
    * **Independent:** Tests should not rely on the order of execution or external state.
    * **Descriptive Naming:** Test function/method names should clearly indicate what they are testing (e.g., `test_user_creation_success`, `it_should_render_user_profile_data`).
* **Running Tests:** Agents should run `npm test` in `frontend/` and `pytest` in `backend/` to validate their changes.

## 4. Error Handling

Implement consistent error handling across the application.

* **Frontend:**
    * Handle API errors gracefully (e.g., display user-friendly messages).
    * Use `try...catch` for asynchronous operations.
    * Centralize error reporting if applicable (e.g., to a logging service).
* **Backend:**
    * Use Python exceptions for internal error signaling.
    * API endpoints should return appropriate HTTP status codes (e.g., 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error) with descriptive JSON error bodies.
    * Log internal errors to aid debugging.

## 5. Security Considerations

Basic security practices must be integrated into development.

* **Input Validation:** Always validate all user inputs on both frontend and backend to prevent common vulnerabilities (e.g., XSS, SQL Injection).
* **Authentication/Authorization:** Ensure proper checks for user authentication and authorization before allowing access to resources.
* **Sensitive Data:** Never hardcode sensitive information (API keys, database credentials) directly into code. Use environment variables (e.g., via `.env` files and `python-dotenv` for backend, or React Native config methods for frontend).
* **Dependency Management:** Regularly update dependencies to patch known vulnerabilities.

## 6. Tool Usage & Build Process

* **Installation:** When setting up an environment, run `npm install` in `frontend/` and `pip install -r requirements.txt` in `backend/`.
* **Running Dev Servers:**
    * `cd frontend && npm start`
    * `cd backend && python run.py` (or `flask run` if appropriate in the future)
* **CI/CD:** Understand that changes will be validated by the `.github/workflows/ci.yml` pipeline. Ensure changes don't break the CI.

## 7. Pull Request & Code Review Expectations

When an agent proposes changes (via a Pull Request), the following are expected:

* **Descriptive Title:** Clearly state the purpose of the PR (e.g., `feat: Implement User Profile View` or `fix: Resolve Login Bug`).
* **Detailed Description:**
    * What problem does this PR solve?
    * What changes were made?
    * How were the changes tested? (Reference specific tests.)
    * Any known limitations or future work.
* **Focused Changes:** PRs should ideally focus on a single feature or bug fix to facilitate review.
* **Passing Tests:** All tests (frontend and backend) must pass.
* **Clean Commit History:** Meaningful commit messages.

## 8. Debugging & Troubleshooting

When encountering issues, agents should:

* **Consult Logs:** Analyze error messages from console or backend logs.
* **Review Tests:** Examine existing tests or write new diagnostic tests to pinpoint issues.
* **Isolate Problem:** Try to narrow down the problem to the smallest possible reproducible case.
* **Utilize Documentation:** Refer to `README.md`, `AGENTS.md`, and code comments.

---