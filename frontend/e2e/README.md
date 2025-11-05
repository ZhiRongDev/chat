# E2E Tests for Chat Application

This directory contains end-to-end (E2E) tests for the chat application using Playwright.

## Test Structure

```
e2e/
├── chat.spec.ts              # Tests for main chat interface
├── authentication.spec.ts     # Tests for login/register flows
├── sidebar.spec.ts           # Tests for sidebar functionality
├── chat-settings.spec.ts     # Tests for settings modal
├── document-manager.spec.ts  # Tests for document management
├── fixtures.ts               # Custom fixtures and helper functions
└── README.md                 # This file
```

## Running Tests

### Run all tests
```bash
npm run test:e2e
```

### Run tests in specific browser
```bash
npm run test:e2e -- --project=chromium
npm run test:e2e -- --project=firefox
npm run test:e2e -- --project=webkit
```

### Run specific test file
```bash
npm run test:e2e -- chat.spec.ts
npm run test:e2e -- authentication.spec.ts
```

### Run tests in headed mode (see browser)
```bash
npm run test:e2e -- --headed
```

### Run tests in debug mode
```bash
npm run test:e2e -- --debug
```

### Run tests in UI mode (interactive)
```bash
npx playwright test --ui
```

## Test Coverage

### 1. Chat Interface (`chat.spec.ts`)
- Initial page load and layout
- Welcome message display
- Message input and sending
- User/bot message display
- Message layout and styling
- RAG mode indicator
- Loading states
- Typing indicators

### 2. Authentication (`authentication.spec.ts`)
- Login modal opening/closing
- Register modal opening/closing
- Form field validation
- Required fields
- Password confirmation matching
- Authentication state management
- User info display
- Logout functionality
- Form clearing on modal close

### 3. Sidebar (`sidebar.spec.ts`)
- Sidebar visibility and toggling
- New chat button functionality
- Chat history display
- User authentication states
- Login/Register/Settings buttons
- User avatar and info display
- Sidebar styling and layout
- Scrollable content area
- Chat history interactions

### 4. Chat Settings (`chat-settings.spec.ts`)
- Settings modal opening/closing
- RAG settings toggle and configuration
- Top-K and Min Score sliders
- LLM provider selection
- Model configuration
- Temperature settings
- API key inputs
- Document library section
- Upload tab switching
- Settings persistence
- Reset to defaults

### 5. Document Manager (`document-manager.spec.ts`)
- Document upload (file and text)
- Document list display
- Empty states
- Loading states
- Document metadata display
- Status badges
- Document actions (preview, delete)
- Upload tab switching
- Responsive design
- Scrollable document list

## Helper Functions and Fixtures

The `fixtures.ts` file provides custom test fixtures and helper functions to simplify common operations:

### Custom Fixtures

- **authenticatedPage**: Pre-authenticated page ready for testing
- **settingsModal**: Page with settings modal already open

### Helper Functions

- `loginUser()`: Simulate user login
- `logout()`: Clear authentication
- `openSettings()`: Open settings modal
- `closeModal()`: Close any modal
- `sendMessage()`: Send a chat message
- `enableRagMode()`: Enable RAG with custom settings
- `setApiKey()`: Set API key for a provider
- `getChatMessages()`: Get all chat messages
- `toggleSidebar()`: Toggle sidebar visibility
- `createNewChat()`: Start a new chat
- `mockApiResponse()`: Mock API responses
- And more...

### Using Fixtures

```typescript
import { test, expect, helpers } from './fixtures';

test('test with authenticated user', async ({ authenticatedPage }) => {
  // Page is already logged in
  await helpers.sendMessage(authenticatedPage, 'Hello');
});

test('test with settings open', async ({ settingsModal }) => {
  // Settings modal is already open
  const ragToggle = settingsModal.locator('#ragToggle');
  await ragToggle.click();
});
```

### Using Helper Functions

```typescript
import { test, expect, helpers } from '@playwright/test';
import { helpers } from './fixtures';

test('send message and check response', async ({ page }) => {
  await page.goto('/');
  await helpers.sendMessage(page, 'Hello');
  await helpers.waitForChatResponse(page);

  const messages = await helpers.getChatMessages(page);
  expect(messages.length).toBeGreaterThan(1);
});
```

## Test Best Practices

### 1. Use Data Test IDs
Prefer using data-testid attributes over CSS selectors when possible:
```typescript
// Good
await page.getByTestId('send-button').click();

// Acceptable
await page.locator('.send-btn').click();
```

### 2. Wait for Elements Properly
Always wait for elements to be visible before interacting:
```typescript
await expect(page.locator('.modal')).toBeVisible();
```

### 3. Clean Up State
Use `beforeEach` to ensure clean state:
```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());
});
```

### 4. Mock API Calls
For reliable tests, mock API responses:
```typescript
await helpers.mockApiResponse(page, /\/api\/v1\/chat/, {
  response: 'Mocked response'
});
```

### 5. Use Custom Fixtures
Leverage custom fixtures to reduce boilerplate:
```typescript
test('test name', async ({ authenticatedPage }) => {
  // No need to manually login
});
```

## Writing New Tests

When adding new tests:

1. Choose the appropriate test file or create a new one
2. Use descriptive test names that explain what is being tested
3. Group related tests using `test.describe()`
4. Clean up state in `beforeEach` hooks
5. Use helper functions from `fixtures.ts` to reduce duplication
6. Add comments for complex test logic
7. Mock API calls when appropriate

### Example Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Setup code
  });

  test('should do something specific', async ({ page }) => {
    // Test implementation
    await expect(page.locator('.element')).toBeVisible();
  });

  test('should handle edge case', async ({ page }) => {
    // Edge case test
  });
});
```

## CI/CD Integration

Tests are configured to run in CI environments with:
- Headless mode enabled
- 2 retry attempts
- HTML report generation
- Preview server for production-like testing

The configuration can be found in `playwright.config.ts`.

## Debugging Tests

### Visual Debugging
```bash
npm run test:e2e -- --debug
```

### Generate Trace
```bash
npm run test:e2e -- --trace on
```

Then view the trace:
```bash
npx playwright show-trace trace.zip
```

### Screenshots on Failure
Screenshots are automatically captured on test failure and stored in `test-results/`.

### Video Recording
Enable video recording in `playwright.config.ts`:
```typescript
use: {
  video: 'on-first-retry'
}
```

## Known Limitations

1. **API Mocking**: Many tests require actual backend API responses. Consider implementing comprehensive API mocking for more reliable tests.

2. **Timing Issues**: Some tests may be flaky due to network delays. Use appropriate wait strategies and increase timeouts when necessary.

3. **Authentication**: Tests that require real authentication need a test database or mocked auth endpoints.

4. **File Uploads**: File upload tests are limited without actual file system interactions.

5. **Real-time Features**: Streaming responses and real-time updates may require special handling.

## Future Improvements

- [ ] Add comprehensive API mocking
- [ ] Implement visual regression testing
- [ ] Add accessibility (a11y) tests
- [ ] Create test data factories
- [ ] Add performance testing
- [ ] Implement cross-browser screenshot comparison
- [ ] Add mobile device testing
- [ ] Create CI/CD pipeline integration
- [ ] Add code coverage reporting for E2E tests

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright Test API](https://playwright.dev/docs/api/class-test)
- [Writing Locators](https://playwright.dev/docs/locators)
