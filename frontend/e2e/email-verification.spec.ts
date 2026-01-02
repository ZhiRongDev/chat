import { test, expect } from '@playwright/test';

test.describe('Email Verification Page', () => {
  test('should display error for missing token', async ({ page }) => {
    await page.goto('/verify-email');

    // Should show error state
    await expect(page.locator('.error-icon')).toBeVisible();
    await expect(page.locator('.alert-danger')).toBeVisible();
    await expect(page.locator('.alert-danger')).toContainText('Invalid or missing verification token');
  });

  test('should display title and subtitle', async ({ page }) => {
    await page.goto('/verify-email?token=test-token&username=testuser');

    await expect(page.locator('h2.title')).toContainText('Email Verification');
  });

  test('should show loading state initially with valid token', async ({ page }) => {
    await page.goto('/verify-email?token=test-token&username=testuser');

    // Should show loading spinner
    await expect(page.locator('.spinner-border')).toBeVisible();
    await expect(page.getByText('Please wait while we verify your email')).toBeVisible();
  });

  test('should have Back to Home button', async ({ page }) => {
    await page.goto('/verify-email');

    const backButton = page.locator('button.btn-primary');
    await expect(backButton).toBeVisible();
  });

  test('should navigate to home when clicking button', async ({ page }) => {
    await page.goto('/verify-email');

    const backButton = page.locator('button.btn-primary');
    await backButton.click();

    await expect(page).toHaveURL('/');
  });

  test('should display error state correctly', async ({ page }) => {
    await page.goto('/verify-email');

    // Error icon should be visible
    await expect(page.locator('.error-icon')).toBeVisible();

    // Button should say "Back to Home"
    const button = page.locator('button.btn-primary');
    await expect(button).toContainText('Back to Home');
  });

  test('should have responsive design on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/verify-email?token=test-token&username=testuser');

    const card = page.locator('.verify-email-card');
    await expect(card).toBeVisible();
  });

  test('should have responsive design on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/verify-email?token=test-token&username=testuser');

    const card = page.locator('.verify-email-card');
    await expect(card).toBeVisible();
  });

  test('should display card with proper styling', async ({ page }) => {
    await page.goto('/verify-email');

    const card = page.locator('.verify-email-card');
    await expect(card).toBeVisible();

    const header = page.locator('.card-header');
    await expect(header).toBeVisible();

    const body = page.locator('.card-body');
    await expect(body).toBeVisible();
  });

  test('should check URL query parameters', async ({ page }) => {
    await page.goto('/verify-email?token=abc123&username=testuser');

    // The page should try to verify (even if it fails due to invalid token)
    // Check that spinner appeared at some point
    const hasLoadingState = await page.locator('.spinner-border').isVisible().catch(() => false);
    const hasErrorState = await page.locator('.error-icon').isVisible();

    // Should be in either loading or error state
    expect(hasLoadingState || hasErrorState).toBe(true);
  });
});
