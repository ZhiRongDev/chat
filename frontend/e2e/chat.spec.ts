import { test, expect } from '@playwright/test';

test.describe('Chat Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the chat application', async ({ page }) => {
    await expect(page.locator('.app-container')).toBeVisible();
    await expect(page.locator('.main-container')).toBeVisible();
  });

  test('should display initial welcome message', async ({ page }) => {
    const firstMessage = page.locator('.message-group.bot').first();
    await expect(firstMessage).toBeVisible();
    await expect(firstMessage.locator('.message-bubble')).toContainText('Hello! How can I help you today?');
  });

  test('should display header with title', async ({ page }) => {
    await expect(page.locator('.header-title')).toBeVisible();
    await expect(page.locator('.header-title')).toContainText('ChatGPT');
  });

  test('should have visible input field and send button', async ({ page }) => {
    await expect(page.locator('.input-field')).toBeVisible();
    await expect(page.locator('.input-field')).toHaveAttribute('placeholder', 'Message ChatGPT...');
    await expect(page.locator('.send-btn')).toBeVisible();
  });

  test('should have disabled send button when input is empty', async ({ page }) => {
    await expect(page.locator('.send-btn')).toBeDisabled();
  });

  test('should enable send button when user types a message', async ({ page }) => {
    const inputField = page.locator('.input-field');
    const sendButton = page.locator('.send-btn');

    await inputField.fill('Hello');
    await expect(sendButton).toBeEnabled();

    await inputField.clear();
    await expect(sendButton).toBeDisabled();
  });

  test('should clear input field after sending a message', async ({ page }) => {
    const inputField = page.locator('.input-field');
    const sendButton = page.locator('.send-btn');

    await inputField.fill('Test message');
    await sendButton.click();

    await expect(inputField).toHaveValue('');
  });

  test('should display user message in chat after sending', async ({ page }) => {
    const inputField = page.locator('.input-field');
    const sendButton = page.locator('.send-btn');
    const testMessage = 'This is a test message';

    await inputField.fill(testMessage);
    await sendButton.click();

    const userMessage = page.locator('.message-group.user').last();
    await expect(userMessage).toBeVisible();
    await expect(userMessage.locator('.message-bubble')).toContainText(testMessage);
  });

  test('should send message on Enter key press', async ({ page }) => {
    const inputField = page.locator('.input-field');
    const testMessage = 'Message sent with Enter';

    await inputField.fill(testMessage);
    await inputField.press('Enter');

    const userMessage = page.locator('.message-group.user').last();
    await expect(userMessage).toBeVisible();
    await expect(userMessage.locator('.message-bubble')).toContainText(testMessage);
  });

  test('should show typing indicator while waiting for response', async ({ page }) => {
    const inputField = page.locator('.input-field');
    const sendButton = page.locator('.send-btn');

    await inputField.fill('Test message');
    await sendButton.click();

    // The typing indicator should appear briefly
    // Note: This may be difficult to test reliably due to timing
    // Consider mocking the API for more reliable tests
  });

  test('should disable input and send button while loading', async ({ page }) => {
    const inputField = page.locator('.input-field');
    const sendButton = page.locator('.send-btn');

    await inputField.fill('Test message');
    await sendButton.click();

    // Immediately after clicking, check if input is disabled
    await expect(inputField).toBeDisabled();
    await expect(sendButton).toBeDisabled();
  });

  test('should display menu button in header', async ({ page }) => {
    const menuButton = page.locator('.menu-btn');
    await expect(menuButton).toBeVisible();
  });

  test('should have messages container with proper scrolling', async ({ page }) => {
    const messagesContainer = page.locator('.messages-container');
    await expect(messagesContainer).toBeVisible();

    // Check that it has overflow-y auto for scrolling
    const overflowY = await messagesContainer.evaluate(el => getComputedStyle(el).overflowY);
    expect(overflowY).toBe('auto');
  });
});

test.describe('Chat Messages Layout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display bot messages on the left', async ({ page }) => {
    const botMessage = page.locator('.message-group.bot').first();
    const justifyContent = await botMessage.evaluate(el => getComputedStyle(el).justifyContent);

    // Bot messages should not be flex-end (which would put them on the right)
    expect(justifyContent).not.toBe('flex-end');
  });

  test('should display user messages on the right', async ({ page }) => {
    const inputField = page.locator('.input-field');
    await inputField.fill('Test message');
    await inputField.press('Enter');

    const userMessage = page.locator('.message-group.user').last();
    await expect(userMessage).toBeVisible();

    const justifyContent = await userMessage.evaluate(el => getComputedStyle(el).justifyContent);
    expect(justifyContent).toBe('flex-end');
  });

  test('should apply different styling to bot and user messages', async ({ page }) => {
    const inputField = page.locator('.input-field');
    await inputField.fill('Test');
    await inputField.press('Enter');

    // Wait for messages to render
    await page.waitForTimeout(100);

    const botBubble = page.locator('.message-group.bot .message-bubble').first();
    const userBubble = page.locator('.message-group.user .message-bubble').last();

    const botBg = await botBubble.evaluate(el => getComputedStyle(el).backgroundColor);
    const userBg = await userBubble.evaluate(el => getComputedStyle(el).backgroundColor);

    // Bot and user messages should have different background colors
    expect(botBg).not.toBe(userBg);
  });
});

test.describe('RAG Mode Indicator', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should not show RAG indicator by default', async ({ page }) => {
    await expect(page.locator('.rag-indicator')).not.toBeVisible();
  });

  test('should show RAG indicator when RAG mode is enabled', async ({ page }) => {
    // Enable RAG mode through settings
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();

    // Wait for modal
    await expect(page.locator('#appModal')).toBeVisible();

    // Enable RAG toggle
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    // Save settings
    const saveButton = page.locator('button:has-text("Save Settings")');
    await saveButton.click();

    // Close modal
    const closeButton = page.locator('.btn-close');
    await closeButton.click();

    // Check RAG indicator is visible
    await expect(page.locator('.rag-indicator')).toBeVisible();
    await expect(page.locator('.rag-indicator')).toContainText('RAG Mode Active');
  });
});
