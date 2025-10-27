import { test, expect } from '@playwright/test';

test.describe('Chat Application', () => {
  test('visits the app root url', async ({ page }) => {
    await page.goto('/');
    // Check that the chat interface loads
    await expect(page.locator('.app-container')).toBeVisible();
  });

  test('displays chat interface', async ({ page }) => {
    await page.goto('/');
    // Check for main chat elements
    await expect(page.locator('.sidebar')).toBeVisible();
    await expect(page.locator('.messages-container')).toBeVisible();
    await expect(page.locator('.input-area')).toBeVisible();
  });

  test('shows initial bot message', async ({ page }) => {
    await page.goto('/');
    // Wait for messages to load
    await page.waitForSelector('.message-group');
    // Check for welcome message
    const messages = page.locator('.message-group');
    await expect(messages.first()).toBeVisible();
  });

  test('can open settings modal', async ({ page }) => {
    await page.goto('/');
    // Click settings button
    await page.click('button:has-text("Settings")');
    // Check modal is visible
    await expect(page.locator('.modal-overlay')).toBeVisible();
    await expect(page.locator('text=Chat Settings')).toBeVisible();
  });

  test('sidebar can be toggled', async ({ page }) => {
    await page.goto('/');
    // Check sidebar is visible initially
    const sidebar = page.locator('.sidebar');
    await expect(sidebar).toBeVisible();

    // Click menu button to toggle
    await page.click('.menu-btn');
    // Sidebar should have hidden class
    await expect(sidebar).toHaveClass(/hidden/);
  });
})
