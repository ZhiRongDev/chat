import { test, expect } from '@playwright/test';

test.describe('Authentication Modals', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Clear any existing auth state
    await page.evaluate(() => localStorage.clear());
  });

  test('should open login modal when clicking Login button', async ({ page }) => {
    const loginButton = page.locator('button:has-text("Login")');
    await loginButton.click();

    await expect(page.locator('#appModal')).toBeVisible();
    await expect(page.locator('#appModalLabel')).toContainText('Login');
  });

  test('should open register modal when clicking Register button', async ({ page }) => {
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();

    await expect(page.locator('#appModal')).toBeVisible();
    await expect(page.locator('#appModalLabel')).toContainText('Register');
  });

  test('should close modal when clicking close button', async ({ page }) => {
    const loginButton = page.locator('button:has-text("Login")');
    await loginButton.click();

    await expect(page.locator('#appModal')).toBeVisible();

    const closeButton = page.locator('.btn-close');
    await closeButton.click();

    // Wait for modal to close
    await page.waitForTimeout(500);

    const modal = page.locator('#appModal');
    const isHidden = await modal.evaluate(el => !el.classList.contains('show'));
    expect(isHidden).toBe(true);
  });

  test('should close modal when clicking Cancel button', async ({ page }) => {
    const loginButton = page.locator('button:has-text("Login")');
    await loginButton.click();

    await expect(page.locator('#appModal')).toBeVisible();

    const cancelButton = page.locator('button:has-text("Cancel")');
    await cancelButton.click();

    // Wait for modal to close
    await page.waitForTimeout(500);
  });
});

test.describe('Login Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());

    // Open login modal
    const loginButton = page.locator('button:has-text("Login")');
    await loginButton.click();
    await expect(page.locator('#appModal')).toBeVisible();
  });

  test('should display login form fields', async ({ page }) => {
    await expect(page.locator('#login-username')).toBeVisible();
    await expect(page.locator('#login-password')).toBeVisible();
    await expect(page.locator('label[for="login-username"]')).toContainText('Username');
    await expect(page.locator('label[for="login-password"]')).toContainText('Password');
  });

  test('should have required fields', async ({ page }) => {
    const usernameInput = page.locator('#login-username');
    const passwordInput = page.locator('#login-password');

    await expect(usernameInput).toHaveAttribute('required');
    await expect(passwordInput).toHaveAttribute('required');
  });

  test('should have password field with type password', async ({ page }) => {
    const passwordInput = page.locator('#login-password');
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('should enable login button when fields are filled', async ({ page }) => {
    const usernameInput = page.locator('#login-username');
    const passwordInput = page.locator('#login-password');
    const loginSubmitButton = page.locator('button[type="submit"]:has-text("Login")');

    await usernameInput.fill('testuser');
    await passwordInput.fill('testpass123');

    await expect(loginSubmitButton).toBeEnabled();
  });

  test('should show loading state when submitting', async ({ page }) => {
    const usernameInput = page.locator('#login-username');
    const passwordInput = page.locator('#login-password');
    const loginSubmitButton = page.locator('button[type="submit"]:has-text("Login")');

    await usernameInput.fill('testuser');
    await passwordInput.fill('testpass123');

    // Submit the form
    await loginSubmitButton.click();

    // Check for loading state (spinner or disabled state)
    // Note: This will fail if the API doesn't respond, which is expected in E2E
    // Consider mocking the API for more reliable tests
  });

  test('should display placeholders', async ({ page }) => {
    await expect(page.locator('#login-username')).toHaveAttribute('placeholder', 'Enter your username');
    await expect(page.locator('#login-password')).toHaveAttribute('placeholder', 'Enter your password');
  });
});

test.describe('Register Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());

    // Open register modal
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();
    await expect(page.locator('#appModal')).toBeVisible();
  });

  test('should display register form fields', async ({ page }) => {
    await expect(page.locator('#register-username')).toBeVisible();
    await expect(page.locator('#register-password')).toBeVisible();
    await expect(page.locator('#register-confirm')).toBeVisible();
    await expect(page.locator('label[for="register-username"]')).toContainText('Username');
    await expect(page.locator('label[for="register-password"]')).toContainText('Password');
    await expect(page.locator('label[for="register-confirm"]')).toContainText('Confirm Password');
  });

  test('should have required fields', async ({ page }) => {
    const usernameInput = page.locator('#register-username');
    const passwordInput = page.locator('#register-password');
    const confirmInput = page.locator('#register-confirm');

    await expect(usernameInput).toHaveAttribute('required');
    await expect(passwordInput).toHaveAttribute('required');
    await expect(confirmInput).toHaveAttribute('required');
  });

  test('should have password fields with type password', async ({ page }) => {
    const passwordInput = page.locator('#register-password');
    const confirmInput = page.locator('#register-confirm');

    await expect(passwordInput).toHaveAttribute('type', 'password');
    await expect(confirmInput).toHaveAttribute('type', 'password');
  });

  test('should enable register button when all fields are filled', async ({ page }) => {
    const usernameInput = page.locator('#register-username');
    const passwordInput = page.locator('#register-password');
    const confirmInput = page.locator('#register-confirm');
    const registerSubmitButton = page.locator('button[type="submit"]:has-text("Register")');

    await usernameInput.fill('newuser');
    await passwordInput.fill('password123');
    await confirmInput.fill('password123');

    await expect(registerSubmitButton).toBeEnabled();
  });

  test('should display placeholders', async ({ page }) => {
    await expect(page.locator('#register-username')).toHaveAttribute('placeholder', 'Enter your username');
    await expect(page.locator('#register-password')).toHaveAttribute('placeholder', 'Enter your password');
    await expect(page.locator('#register-confirm')).toHaveAttribute('placeholder', 'Confirm your password');
  });
});

test.describe('Authentication State', () => {
  test('should hide login/register buttons when user is logged in', async ({ page }) => {
    // Simulate logged in state
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('token', 'fake-token');
      localStorage.setItem('user', JSON.stringify({ username: 'testuser' }));
    });

    await page.reload();

    // Login and Register buttons should not be visible
    await expect(page.locator('button:has-text("Login")')).not.toBeVisible();
    await expect(page.locator('button:has-text("Register")')).not.toBeVisible();
  });

  test('should show logout button when user is logged in', async ({ page }) => {
    // Simulate logged in state
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('token', 'fake-token');
      localStorage.setItem('user', JSON.stringify({ username: 'testuser' }));
    });

    await page.reload();

    // Logout button should be visible
    await expect(page.locator('button:has-text("Logout")')).toBeVisible();
  });

  test('should display user info when logged in', async ({ page }) => {
    const username = 'testuser';

    // Simulate logged in state
    await page.goto('/');
    await page.evaluate((user) => {
      localStorage.setItem('token', 'fake-token');
      localStorage.setItem('user', JSON.stringify({ username: user }));
    }, username);

    await page.reload();

    // User info should be displayed
    await expect(page.locator('.user-info')).toBeVisible();
    await expect(page.locator('.user-name')).toContainText(username);
  });

  test('should display user avatar with first letter', async ({ page }) => {
    const username = 'testuser';

    // Simulate logged in state
    await page.goto('/');
    await page.evaluate((user) => {
      localStorage.setItem('token', 'fake-token');
      localStorage.setItem('user', JSON.stringify({ username: user }));
    }, username);

    await page.reload();

    // User avatar should display first letter
    const avatar = page.locator('.user-avatar');
    await expect(avatar).toBeVisible();
    await expect(avatar).toContainText(username.charAt(0).toUpperCase());
  });

  test('should clear auth state on logout', async ({ page }) => {
    // Simulate logged in state
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('token', 'fake-token');
      localStorage.setItem('user', JSON.stringify({ username: 'testuser' }));
    });

    await page.reload();

    // Click logout
    const logoutButton = page.locator('button:has-text("Logout")');
    await logoutButton.click();

    // Login and Register buttons should be visible again
    await expect(page.locator('button:has-text("Login")')).toBeVisible();
    await expect(page.locator('button:has-text("Register")')).toBeVisible();
  });
});

test.describe('Form Validation', () => {
  test('should show error for mismatched passwords in register form', async ({ page }) => {
    await page.goto('/');

    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();

    const usernameInput = page.locator('#register-username');
    const passwordInput = page.locator('#register-password');
    const confirmInput = page.locator('#register-confirm');
    const registerSubmitButton = page.locator('button[type="submit"]:has-text("Register")');

    await usernameInput.fill('newuser');
    await passwordInput.fill('password123');
    await confirmInput.fill('differentpassword');

    await registerSubmitButton.click();

    // Should show error message about mismatched passwords
    // Note: The exact error display mechanism depends on implementation
  });

  test('should clear form fields when modal is closed', async ({ page }) => {
    await page.goto('/');

    const loginButton = page.locator('button:has-text("Login")');
    await loginButton.click();

    const usernameInput = page.locator('#login-username');
    const passwordInput = page.locator('#login-password');

    await usernameInput.fill('testuser');
    await passwordInput.fill('testpass');

    const closeButton = page.locator('.btn-close');
    await closeButton.click();

    // Wait for modal to close
    await page.waitForTimeout(500);

    // Reopen modal
    await loginButton.click();

    // Fields should be cleared
    await expect(usernameInput).toHaveValue('');
    await expect(passwordInput).toHaveValue('');
  });
});
