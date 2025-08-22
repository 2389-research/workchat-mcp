# WorkChat E2E Tests

End-to-end tests for WorkChat using Playwright.

## Test Structure

### Test Files

- **`setup.spec.ts`** - Basic setup and environment verification tests
- **`chat-flow.spec.ts`** - Core chat functionality tests (channel selection, messaging)
- **`real-time-updates.spec.ts`** - Real-time SSE and multi-user scenarios
- **`integration.spec.ts`** - Comprehensive integration tests and user journeys

### Helper Files

- **`helpers/test-utils.ts`** - Common test utilities and page object methods

## Running Tests

### Prerequisites

1. Backend server running at `http://localhost:8000`
2. Frontend dev server running at `http://localhost:3000`

### Local Development

```bash
# Install dependencies (if not already done)
npm ci

# Install Playwright browsers
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run tests with UI mode (interactive)
npm run test:e2e:ui

# Run specific test file
npx playwright test chat-flow.spec.ts

# Run tests in headed mode (see browser)
npx playwright test --headed
```

### CI/CD

Tests run automatically in GitHub Actions on push/PR. The CI pipeline:

1. Sets up both backend (Python/FastAPI) and frontend (Node.js)
2. Installs Playwright browsers
3. Runs all E2E tests in headless mode
4. Uploads test reports as artifacts

## Test Scenarios

### Scenario 1: Basic Chat Flow
- User loads the application
- Browses channels in sidebar
- Selects a channel
- Views message thread
- Composes and sends a message

### Scenario 2: Real-time Updates
- Two browser contexts (simulating multiple users)
- Both connect to SSE stream
- Verify real-time message updates
- Test connection recovery

### Integration Tests
- Complete user journeys
- Keyboard navigation and shortcuts
- Responsive design testing
- Error handling and edge cases
- Performance benchmarks

## Configuration

Tests are configured via `playwright.config.ts`:

- **Base URL**: `http://localhost:3000`
- **Browsers**: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari
- **Reporters**: HTML report with screenshots on failure
- **Web Servers**: Auto-starts backend and frontend servers
- **Timeouts**: Reasonable defaults with retries on CI

## Best Practices

### Test Design
- Use Page Object Model via `test-utils.ts`
- Focus on user journeys rather than implementation details
- Test both happy path and error scenarios
- Include accessibility testing

### Maintenance
- Keep tests independent and isolated
- Use data attributes for stable element selection
- Mock external dependencies when needed
- Regular test review and cleanup

### Debugging
- Use `--headed` mode to see browser actions
- Add `await page.pause()` for interactive debugging
- Check `playwright-report/` for detailed failure reports
- Use browser dev tools with `page.evaluate()`

## Limitations

Since WorkChat uses JWT authentication, some test scenarios are limited without proper login:

- **Channel Creation**: Requires admin authentication
- **Message Persistence**: Needs authenticated user context
- **Real-time Events**: Limited without backend message flow

Tests focus on UI behavior, component integration, and client-side functionality that can be verified without full authentication flow.

## Future Enhancements

- Add authentication test fixtures
- Mock backend responses for isolated frontend testing
- Performance testing with load simulation
- Visual regression testing
- Accessibility audit integration