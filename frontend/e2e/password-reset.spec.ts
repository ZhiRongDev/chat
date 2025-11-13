import { test, expect } from '@playwright/test';

test.describe('Password Reset Page', () => {
  test('should display error for missing token', async ({ page }) => {
    await page.goto('/reset-password');

    await expect(page.locator('.alert-danger')).toBeVisible();
    await expect(page.locator('.alert-danger')).toContainText('Invalid or missing reset token');
  });

  test('should display form with token present', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    await expect(page.locator('h2')).toContainText('Reset Password');
    await expect(page.locator('#new-password')).toBeVisible();
    await expect(page.locator('#confirm-password')).toBeVisible();
  });

  test('should have password fields of type password', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    const newPasswordField = page.locator('#new-password');
    const confirmPasswordField = page.locator('#confirm-password');

    await expect(newPasswordField).toHaveAttribute('type', 'password');
    await expect(confirmPasswordField).toHaveAttribute('type', 'password');
  });

  test('should toggle password visibility', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    const newPasswordField = page.locator('#new-password');
    const toggleButton = page.locator('.password-toggle-btn').first();

    // Initially should be password type
    await expect(newPasswordField).toHaveAttribute('type', 'password');

    // Click toggle
    await toggleButton.click();

    // Should now be text type
    await expect(newPasswordField).toHaveAttribute('type', 'text');

    // Click again to toggle back
    await toggleButton.click();
    await expect(newPasswordField).toHaveAttribute('type', 'password');
  });

  test('should show error for empty fields', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // HTML5 validation should prevent submission
    const newPasswordField = page.locator('#new-password');
    const isRequired = await newPasswordField.evaluate((el: HTMLInputElement) => el.required);
    expect(isRequired).toBe(true);
  });

  test('should show error for mismatched passwords', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    await page.locator('#new-password').fill('password123');
    await page.locator('#confirm-password').fill('differentpassword');

    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    await expect(page.locator('.alert-danger')).toBeVisible();
    await expect(page.locator('.alert-danger')).toContainText('do not match');
  });

  test('should show error for short password', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    await page.locator('#new-password').fill('12345');
    await page.locator('#confirm-password').fill('12345');

    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    await expect(page.locator('.alert-danger')).toBeVisible();
    await expect(page.locator('.alert-danger')).toContainText('at least 6 characters');
  });

  test('should have Back to Home button', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    const backButton = page.locator('button.btn-secondary');
    await expect(backButton).toBeVisible();
    await expect(backButton).toContainText('Back to Home');
  });

  test('should navigate to home when clicking Back to Home', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    const backButton = page.locator('button.btn-secondary');
    await backButton.click();

    await expect(page).toHaveURL('/');
  });

  test('should disable form during submission', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    await page.locator('#new-password').fill('newpassword123');
    await page.locator('#confirm-password').fill('newpassword123');

    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // Button should show loading state
    await expect(submitButton).toContainText('Resetting...');
  });

  test('should have required fields marked', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    const newPasswordField = page.locator('#new-password');
    const confirmPasswordField = page.locator('#confirm-password');

    await expect(newPasswordField).toHaveAttribute('required');
    await expect(confirmPasswordField).toHaveAttribute('required');
  });

  test('should display placeholder text', async ({ page }) => {
    await page.goto('/reset-password?token=test-token&username=testuser');

    await expect(page.locator('#new-password')).toHaveAttribute('placeholder', 'Enter your new password');
    await expect(page.locator('#confirm-password')).toHaveAttribute('placeholder', 'Confirm your new password');
  });

  test('should have responsive design on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/reset-password?token=test-token&username=testuser');

    const card = page.locator('.reset-password-card');
    await expect(card).toBeVisible();
  });
});
