# Testing Documentation

This document provides comprehensive information about the testing infrastructure for the RAG Chat Application.

## Table of Contents

- [Overview](#overview)
- [Backend Tests](#backend-tests)
- [Frontend Tests](#frontend-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Running Tests Locally](#running-tests-locally)
- [Test Coverage](#test-coverage)
- [Best Practices](#best-practices)

## Overview

The project uses a comprehensive testing strategy with:
- **Backend**: pytest for unit and integration tests
- **Frontend**: Vitest for unit tests, Playwright for E2E tests
- **CI/CD**: GitHub Actions for automated testing

## Backend Tests

### Test Structure

```
backend/
├── tests/
│   ├── conftest.py           # Pytest fixtures and configuration
│   ├── test_auth.py          # Authentication endpoint tests
│   ├── test_user_service.py  # User service unit tests
│   ├── test_chat_router.py   # Chat router endpoint tests
│   ├── test_chat_service.py  # Chat service unit tests
│   └── test_document_router.py # Document router endpoint tests
└── pytest.ini                # Pytest configuration
```

### Test Types

#### Unit Tests
- Marked with `@pytest.mark.unit`
- Test individual functions and classes in isolation
- Use mocked dependencies

#### Integration Tests
- Marked with `@pytest.mark.integration`
- Test API endpoints with TestClient
- Use in-memory SQLite database

### Running Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run in verbose mode
pytest -v
```

### Test Fixtures

Available fixtures (defined in `conftest.py`):
- `session`: In-memory SQLite database session
- `client`: FastAPI TestClient
- `test_user`: Pre-created test user
- `auth_token`: JWT token for test user
- `auth_headers`: Authorization headers for authenticated requests

## Frontend Tests

### Test Structure

```
frontend/
├── e2e/                          # Playwright E2E tests
│   ├── authentication.spec.ts
│   ├── chat.spec.ts
│   ├── chat-settings.spec.ts
│   ├── document-manager.spec.ts
│   ├── sidebar.spec.ts
│   ├── password-reset.spec.ts
│   └── email-verification.spec.ts
├── src/
│   └── __tests__/               # Vitest unit tests
│       ├── user.store.spec.ts
│       └── ChatSettings.spec.ts
├── playwright.config.ts
└── vitest.config.ts
```

### Running Frontend Tests

#### Unit Tests (Vitest)

```bash
cd frontend

# Run unit tests
npm run test:unit

# Run in watch mode
npm run test:unit -- --watch

# Run with coverage
npm run test:unit -- --coverage
```

#### E2E Tests (Playwright)

```bash
cd frontend

# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run in specific browser
npm run test:e2e -- --project=chromium
npm run test:e2e -- --project=firefox
npm run test:e2e -- --project=webkit

# Run specific test file
npm run test:e2e -- tests/authentication.spec.ts

# Run in debug mode
npm run test:e2e -- --debug

# Run in headed mode (see browser)
npm run test:e2e -- --headed

# Show test report
npx playwright show-report
```

### Type Checking

```bash
cd frontend

# Run TypeScript type checking
npm run type-check
```

## CI/CD Pipeline

### GitHub Actions Workflows

The project uses GitHub Actions for continuous integration. The main workflow (`.github/workflows/ci.yml`) includes:

#### Jobs

1. **backend-tests**
   - Runs pytest with PostgreSQL and Redis services
   - Generates coverage reports
   - Uploads coverage to Codecov

2. **frontend-unit-tests**
   - Runs Vitest unit tests
   - Performs TypeScript type checking

3. **frontend-e2e-tests**
   - Runs Playwright E2E tests in Chromium
   - Uploads test reports as artifacts

4. **integration-tests**
   - Full stack testing with backend and frontend
   - Tests complete user flows

5. **lint-and-format**
   - Checks code formatting (Prettier, Black)
   - Runs linters (ESLint, Flake8)

6. **security-scan**
   - Runs Trivy vulnerability scanner
   - Uploads results to GitHub Security tab

7. **build-check**
   - Builds Docker images for backend and frontend
   - Validates Docker configuration

8. **test-summary**
   - Aggregates results from all test jobs
   - Fails if any test job failed

### Triggering CI

CI runs automatically on:
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop` branches

### Viewing Results

- Check the "Actions" tab in GitHub repository
- View test reports in job logs
- Download Playwright reports from artifacts
- Check coverage reports in Codecov (if configured)

## Running Tests Locally

### Prerequisites

**Backend:**
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio

# Set up environment variables
cp .env.template .env
# Edit .env with test database credentials
```

**Frontend:**
```bash
# Install Node.js dependencies
cd frontend
npm install

# Install Playwright browsers
npx playwright install
```

### Docker Compose

Run tests in Docker environment:

```bash
# Start services
docker-compose up -d

# Run backend tests
docker-compose exec backend pytest

# Run frontend tests
docker-compose exec frontend npm run test:unit
```

## Test Coverage

### Backend Coverage

Current coverage (run `pytest --cov=app`):

| Module | Coverage |
|--------|----------|
| app/router/* | ~90% |
| app/service/* | ~85% |
| app/auth.py | ~95% |

### Frontend Coverage

Run `npm run test:unit -- --coverage` to see:
- Statement coverage
- Branch coverage
- Function coverage
- Line coverage

### Coverage Goals

- Maintain >80% overall coverage
- >90% for critical paths (auth, payment, data handling)
- >70% for UI components

## Best Practices

### Writing Tests

1. **Descriptive Names**
   ```python
   # Good
   def test_user_cannot_access_other_users_data():
       ...

   # Bad
   def test_user_data():
       ...
   ```

2. **Arrange-Act-Assert (AAA) Pattern**
   ```python
   def test_create_user():
       # Arrange
       username = "testuser"
       password = "testpass"

       # Act
       user = create_user(username, password)

       # Assert
       assert user.username == username
   ```

3. **Test One Thing**
   - Each test should verify one specific behavior
   - Don't combine multiple test cases

4. **Avoid Test Interdependencies**
   - Tests should be independent
   - Don't rely on execution order

5. **Use Fixtures Appropriately**
   - Reuse common setup with fixtures
   - Keep fixtures focused and simple

### Playwright Best Practices

1. **Use Proper Locators**
   ```typescript
   // Good - specific and stable
   await page.locator('#login-button').click();

   // Bad - fragile
   await page.locator('button').nth(3).click();
   ```

2. **Wait for Conditions**
   ```typescript
   // Good - wait for element to be visible
   await expect(page.locator('.alert')).toBeVisible();

   // Bad - arbitrary timeout
   await page.waitForTimeout(1000);
   ```

3. **Clean Up State**
   ```typescript
   test.beforeEach(async ({ page }) => {
     await page.goto('/');
     await page.evaluate(() => localStorage.clear());
   });
   ```

### Pytest Best Practices

1. **Use Markers**
   ```python
   @pytest.mark.unit
   def test_password_hash():
       ...

   @pytest.mark.integration
   def test_login_endpoint():
       ...
   ```

2. **Mock External Dependencies**
   ```python
   @patch("app.service.external_api.call")
   def test_with_mocked_api(mock_call):
       mock_call.return_value = {"data": "test"}
       ...
   ```

3. **Parameterize Tests**
   ```python
   @pytest.mark.parametrize("password,expected", [
       ("short", False),
       ("longenoughpass", True),
   ])
   def test_password_validation(password, expected):
       assert validate_password(password) == expected
   ```

## Troubleshooting

### Common Issues

#### Playwright Tests Failing

```bash
# Update browsers
npx playwright install

# Clear cache
rm -rf node_modules/.cache

# Run in debug mode
npm run test:e2e -- --debug
```

#### Backend Tests Failing

```bash
# Check database connection
pytest -v tests/test_auth.py

# Clear pytest cache
pytest --cache-clear

# Show full output
pytest -s
```

#### CI Failures

1. Check job logs in GitHub Actions
2. Download artifacts (test reports)
3. Run tests locally with same environment
4. Check for environment-specific issues

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure tests pass locally
3. Check coverage doesn't decrease
4. Follow naming conventions
5. Add appropriate markers
6. Update this documentation if needed

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Best Practices](https://testingjavascript.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
