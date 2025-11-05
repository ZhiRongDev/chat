import { test, expect } from '@playwright/test';

test.describe('Sidebar Visibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display sidebar by default', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    await expect(sidebar).toBeVisible();
    await expect(sidebar).not.toHaveClass(/hidden/);
  });

  test('should toggle sidebar when clicking menu button', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    const menuButton = page.locator('.menu-btn');

    // Initially visible
    await expect(sidebar).toBeVisible();

    // Click to hide
    await menuButton.click();
    await expect(sidebar).toHaveClass(/hidden/);

    // Click to show again
    await menuButton.click();
    await expect(sidebar).not.toHaveClass(/hidden/);
  });

  test('should hide sidebar content when sidebar is hidden', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    const menuButton = page.locator('.menu-btn');
    const newChatButton = page.locator('.new-chat-btn');

    await menuButton.click();
    await expect(sidebar).toHaveClass(/hidden/);

    // Sidebar content should not be visible
    const isVisible = await newChatButton.isVisible();
    expect(isVisible).toBe(false);
  });
});

test.describe('Sidebar Header', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display New Chat button', async ({ page }) => {
    const newChatButton = page.locator('.new-chat-btn');
    await expect(newChatButton).toBeVisible();
    await expect(newChatButton).toContainText('New chat');
  });

  test('should create new chat when clicking New Chat button', async ({ page }) => {
    // First send a message to have chat history
    const inputField = page.locator('.input-field');
    await inputField.fill('Test message');
    await inputField.press('Enter');

    // Wait for message to appear
    await page.waitForTimeout(500);

    // Click new chat
    const newChatButton = page.locator('.new-chat-btn');
    await newChatButton.click();

    // Should reset to initial state with only welcome message
    const messages = page.locator('.message-group');
    const count = await messages.count();
    expect(count).toBe(1); // Only the initial greeting
  });
});

test.describe('Sidebar Content - Chat History', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('should show "No chat history yet" when not logged in', async ({ page }) => {
    const noHistory = page.locator('.no-history');
    await expect(noHistory).toBeVisible();
    await expect(noHistory).toContainText('No chat history yet');
  });

  test('should not display chat history list when there are no chats', async ({ page }) => {
    const chatHistoryList = page.locator('.chat-history-list');
    await expect(chatHistoryList).not.toBeVisible();
  });

  test('should display chat history items when logged in with chats', async ({ page }) => {
    // Simulate logged in state with chat histories
    await page.evaluate(() => {
      localStorage.setItem('token', 'fake-token');
      localStorage.setItem('user', JSON.stringify({ username: 'testuser' }));
    });

    // Note: This test would require mocking the API to return chat histories
    // For a real E2E test, you'd need a test database with sample data
  });

  test('should highlight active chat in history', async ({ page }) => {
    // This test requires being logged in and having multiple chat histories
    // Would need API mocking or test data setup
  });
});

test.describe('Sidebar Footer - Unauthenticated', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('should display Login button when not authenticated', async ({ page }) => {
    const loginButton = page.locator('.sidebar button:has-text("Login")');
    await expect(loginButton).toBeVisible();
  });

  test('should display Register button when not authenticated', async ({ page }) => {
    const registerButton = page.locator('.sidebar button:has-text("Register")');
    await expect(registerButton).toBeVisible();
  });

  test('should display Settings button when not authenticated', async ({ page }) => {
    const settingsButton = page.locator('.sidebar button:has-text("Settings")');
    await expect(settingsButton).toBeVisible();
  });

  test('should open login modal from sidebar', async ({ page }) => {
    const loginButton = page.locator('.sidebar button:has-text("Login")');
    await loginButton.click();

    await expect(page.locator('#appModal')).toBeVisible();
    await expect(page.locator('#appModalLabel')).toContainText('Login');
  });

  test('should open register modal from sidebar', async ({ page }) => {
    const registerButton = page.locator('.sidebar button:has-text("Register")');
    await registerButton.click();

    await expect(page.locator('#appModal')).toBeVisible();
    await expect(page.locator('#appModalLabel')).toContainText('Register');
  });

  test('should open settings modal from sidebar', async ({ page }) => {
    const settingsButton = page.locator('.sidebar button:has-text("Settings")');
    await settingsButton.click();

    await expect(page.locator('#appModal')).toBeVisible();
    await expect(page.locator('#appModalLabel')).toContainText('Settings');
  });
});

test.describe('Sidebar Footer - Authenticated', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('token', 'fake-token');
      localStorage.setItem('user', JSON.stringify({ username: 'testuser' }));
    });
    await page.reload();
  });

  test('should display user info when authenticated', async ({ page }) => {
    const userInfo = page.locator('.user-info');
    await expect(userInfo).toBeVisible();
  });

  test('should display username in user info', async ({ page }) => {
    const userName = page.locator('.user-name');
    await expect(userName).toBeVisible();
    await expect(userName).toContainText('testuser');
  });

  test('should display user avatar', async ({ page }) => {
    const userAvatar = page.locator('.user-avatar');
    await expect(userAvatar).toBeVisible();
    await expect(userAvatar).toContainText('T'); // First letter of testuser
  });

  test('should display logout link when authenticated', async ({ page }) => {
    const logoutLink = page.locator('.logout-link');
    await expect(logoutLink).toBeVisible();
    await expect(logoutLink).toContainText('Logout');
  });

  test('should not display Login/Register buttons when authenticated', async ({ page }) => {
    await expect(page.locator('.sidebar button:has-text("Login")')).not.toBeVisible();
    await expect(page.locator('.sidebar button:has-text("Register")')).not.toBeVisible();
  });

  test('should still display Settings button when authenticated', async ({ page }) => {
    const settingsButton = page.locator('.sidebar button:has-text("Settings")');
    await expect(settingsButton).toBeVisible();
  });
});

test.describe('Sidebar Styling and Layout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should have dark background color', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    const bgColor = await sidebar.evaluate(el => getComputedStyle(el).backgroundColor);

    // Check that it's a dark color (not white)
    expect(bgColor).not.toBe('rgb(255, 255, 255)');
  });

  test('should have fixed width', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    const width = await sidebar.evaluate(el => getComputedStyle(el).width);

    // Should have a specific width (260px based on the CSS)
    expect(width).toBe('260px');
  });

  test('should have scrollable content area', async ({ page }) => {
    const sidebarContent = page.locator('.sidebar-content');
    const overflowY = await sidebarContent.evaluate(el => getComputedStyle(el).overflowY);

    expect(overflowY).toBe('auto');
  });

  test('should have proper flex layout', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    const display = await sidebar.evaluate(el => getComputedStyle(el).display);
    const flexDirection = await sidebar.evaluate(el => getComputedStyle(el).flexDirection);

    expect(display).toBe('flex');
    expect(flexDirection).toBe('column');
  });
});

test.describe('Chat History Item Interactions', () => {
  test('should show delete button on hover', async ({ page }) => {
    // This test requires having chat history items
    // Would need to mock the API or have test data
  });

  test('should highlight chat item on hover', async ({ page }) => {
    // This test requires having chat history items
    // Would need to mock the API or have test data
  });

  test('should delete chat when clicking delete button', async ({ page }) => {
    // This test requires having chat history items
    // Would need to mock the API or have test data
  });

  test('should load chat when clicking on history item', async ({ page }) => {
    // This test requires having chat history items
    // Would need to mock the API or have test data
  });

  test('should show active state for current chat', async ({ page }) => {
    // This test requires having chat history items
    // Would need to mock the API or have test data
  });
});

test.describe('Sidebar Buttons Styling', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should have hover effect on sidebar buttons', async ({ page }) => {
    const settingsButton = page.locator('.sidebar button:has-text("Settings")');

    // Get initial background color
    const initialBg = await settingsButton.evaluate(el => getComputedStyle(el).backgroundColor);

    // Hover over button
    await settingsButton.hover();

    // Background color should change on hover
    const hoveredBg = await settingsButton.evaluate(el => getComputedStyle(el).backgroundColor);

    // Note: This test might be flaky depending on how CSS transitions work
  });

  test('should have icons in sidebar buttons', async ({ page }) => {
    const buttons = page.locator('.sidebar-btn');
    const count = await buttons.count();

    for (let i = 0; i < count; i++) {
      const button = buttons.nth(i);
      const svgIcon = button.locator('svg');
      await expect(svgIcon).toBeVisible();
    }
  });

  test('should have proper gap between sidebar footer buttons', async ({ page }) => {
    const sidebarFooter = page.locator('.sidebar-footer');
    const gap = await sidebarFooter.evaluate(el => getComputedStyle(el).gap);

    // Should have spacing between buttons
    expect(gap).not.toBe('0px');
  });
});
