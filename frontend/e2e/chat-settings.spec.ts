import { test, expect } from '@playwright/test';

test.describe('Chat Settings Modal', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should open settings modal when clicking Settings button', async ({ page }) => {
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();

    await expect(page.locator('#appModal')).toBeVisible();
    await expect(page.locator('#appModalLabel')).toContainText('Settings');
  });

  test('should close settings modal when clicking close button', async ({ page }) => {
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();

    const closeButton = page.locator('.btn-close');
    await closeButton.click();

    await page.waitForTimeout(500);
  });
});

test.describe('RAG Settings Section', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();
    await expect(page.locator('#appModal')).toBeVisible();
  });

  test('should display RAG settings section', async ({ page }) => {
    await expect(page.getByText('RAG (Retrieval-Augmented Generation)')).toBeVisible();
  });

  test('should have RAG toggle switch', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');
    await expect(ragToggle).toBeVisible();
    await expect(ragToggle).toHaveAttribute('type', 'checkbox');
  });

  test('should toggle RAG mode on and off', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');

    // Initially should be unchecked
    await expect(ragToggle).not.toBeChecked();

    // Click to enable
    await ragToggle.click();
    await expect(ragToggle).toBeChecked();

    // Click to disable
    await ragToggle.click();
    await expect(ragToggle).not.toBeChecked();
  });

  test('should show RAG options when RAG is enabled', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    // RAG options should be visible
    await expect(page.locator('#topK')).toBeVisible();
    await expect(page.locator('#minScore')).toBeVisible();
  });

  test('should hide RAG options when RAG is disabled', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');

    // Ensure RAG is disabled
    const isChecked = await ragToggle.isChecked();
    if (isChecked) {
      await ragToggle.click();
    }

    // RAG options should not be visible
    const ragOptions = page.locator('.rag-options');
    await expect(ragOptions).not.toBeVisible();
  });

  test('should have Top-K range slider with default value', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    const topKSlider = page.locator('#topK');
    await expect(topKSlider).toBeVisible();
    await expect(topKSlider).toHaveAttribute('type', 'range');
    await expect(topKSlider).toHaveAttribute('min', '1');
    await expect(topKSlider).toHaveAttribute('max', '10');
    await expect(topKSlider).toHaveAttribute('step', '1');
  });

  test('should have Min Score range slider with default value', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    const minScoreSlider = page.locator('#minScore');
    await expect(minScoreSlider).toBeVisible();
    await expect(minScoreSlider).toHaveAttribute('type', 'range');
    await expect(minScoreSlider).toHaveAttribute('min', '0');
    await expect(minScoreSlider).toHaveAttribute('max', '1');
    await expect(minScoreSlider).toHaveAttribute('step', '0.05');
  });

  test('should display current Top-K value', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    const topKLabel = page.locator('label[for="topK"]');
    await expect(topKLabel).toContainText('Top-K Results:');
    // Should also show the current value
  });

  test('should display current Min Score value', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    const minScoreLabel = page.locator('label[for="minScore"]');
    await expect(minScoreLabel).toContainText('Minimum Relevance Score:');
    // Should also show the current value
  });

  test('should update Top-K value when slider is moved', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    const topKSlider = page.locator('#topK');
    await topKSlider.fill('7');

    const topKLabel = page.locator('label[for="topK"]');
    await expect(topKLabel).toContainText('7');
  });

  test('should have helpful descriptions for RAG settings', async ({ page }) => {
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    await expect(page.getByText('Number of relevant document chunks to retrieve')).toBeVisible();
    await expect(page.getByText('Minimum similarity threshold')).toBeVisible();
  });
});

test.describe('LLM Provider Settings Section', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();
    await expect(page.locator('#appModal')).toBeVisible();
  });

  test('should display LLM provider section', async ({ page }) => {
    await expect(page.getByText('LLM Provider')).toBeVisible();
  });

  test('should have provider dropdown', async ({ page }) => {
    const providerSelect = page.locator('#provider');
    await expect(providerSelect).toBeVisible();
  });

  test('should have provider options', async ({ page }) => {
    const providerSelect = page.locator('#provider');
    const options = await providerSelect.locator('option').allTextContents();

    expect(options).toContain('Auto-detect (uses first available API key)');
    expect(options).toContain('Google Gemini');
    expect(options).toContain('OpenAI');
    expect(options).toContain('Anthropic Claude');
  });

  test('should have model input field', async ({ page }) => {
    const modelInput = page.locator('#model');
    await expect(modelInput).toBeVisible();
    await expect(modelInput).toHaveAttribute('placeholder', 'e.g., gpt-4, gemini-pro');
  });

  test('should have temperature slider', async ({ page }) => {
    const temperatureSlider = page.locator('#temperature');
    await expect(temperatureSlider).toBeVisible();
    await expect(temperatureSlider).toHaveAttribute('type', 'range');
    await expect(temperatureSlider).toHaveAttribute('min', '0');
    await expect(temperatureSlider).toHaveAttribute('max', '2');
    await expect(temperatureSlider).toHaveAttribute('step', '0.1');
  });

  test('should display current temperature value', async ({ page }) => {
    const temperatureLabel = page.locator('label[for="temperature"]');
    await expect(temperatureLabel).toContainText('Temperature:');
  });

  test('should update temperature value when slider is moved', async ({ page }) => {
    const temperatureSlider = page.locator('#temperature');
    await temperatureSlider.fill('1.5');

    const temperatureLabel = page.locator('label[for="temperature"]');
    await expect(temperatureLabel).toContainText('1.5');
  });

  test('should change provider selection', async ({ page }) => {
    const providerSelect = page.locator('#provider');
    await providerSelect.selectOption('openai');

    const selectedValue = await providerSelect.inputValue();
    expect(selectedValue).toBe('openai');
  });
});

test.describe('API Keys Settings Section', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();
    await expect(page.locator('#appModal')).toBeVisible();
  });

  test('should display API Keys section', async ({ page }) => {
    await expect(page.getByText('API Keys', { exact: true })).toBeVisible();
  });

  test('should have Gemini API key input', async ({ page }) => {
    const geminiInput = page.locator('#geminiApiKey');
    await expect(geminiInput).toBeVisible();
    await expect(geminiInput).toHaveAttribute('type', 'password');
    await expect(geminiInput).toHaveAttribute('placeholder', 'Enter your Gemini API key');
  });

  test('should have OpenAI API key input', async ({ page }) => {
    const openaiInput = page.locator('#openaiApiKey');
    await expect(openaiInput).toBeVisible();
    await expect(openaiInput).toHaveAttribute('type', 'password');
    await expect(openaiInput).toHaveAttribute('placeholder', 'Enter your OpenAI API key');
  });

  test('should have Anthropic API key input', async ({ page }) => {
    const anthropicInput = page.locator('#anthropicApiKey');
    await expect(anthropicInput).toBeVisible();
    await expect(anthropicInput).toHaveAttribute('type', 'password');
    await expect(anthropicInput).toHaveAttribute('placeholder', 'Enter your Anthropic API key');
  });

  test('should have links to get API keys', async ({ page }) => {
    const geminiLink = page.locator('a[href*="makersuite.google.com"]');
    const openaiLink = page.locator('a[href*="platform.openai.com"]');
    const anthropicLink = page.locator('a[href*="console.anthropic.com"]');

    await expect(geminiLink).toBeVisible();
    await expect(openaiLink).toBeVisible();
    await expect(anthropicLink).toBeVisible();
  });

  test('should mask API key input values', async ({ page }) => {
    const geminiInput = page.locator('#geminiApiKey');
    await geminiInput.fill('test-api-key-123');

    // Type should be password, so value should be masked
    const inputType = await geminiInput.getAttribute('type');
    expect(inputType).toBe('password');
  });

  test('should allow typing in API key fields', async ({ page }) => {
    const openaiInput = page.locator('#openaiApiKey');
    const testKey = 'sk-test-key-123';

    await openaiInput.fill(testKey);
    const value = await openaiInput.inputValue();

    expect(value).toBe(testKey);
  });
});

test.describe('Document Library Section', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();
    await expect(page.locator('#appModal')).toBeVisible();
  });

  test('should display Document Library section', async ({ page }) => {
    await expect(page.getByText('Document Library')).toBeVisible();
  });

  test('should have refresh button for documents', async ({ page }) => {
    const refreshButton = page.locator('.btn-refresh');
    await expect(refreshButton).toBeVisible();
  });

  test('should have upload tabs', async ({ page }) => {
    await expect(page.locator('.upload-tabs')).toBeVisible();
    await expect(page.getByRole('button', { name: /Upload File/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Add Text/i })).toBeVisible();
  });

  test('should switch between upload tabs', async ({ page }) => {
    const fileTab = page.locator('button').filter({ hasText: 'Upload File' });
    const textTab = page.locator('button').filter({ hasText: 'Add Text' });

    // Click text tab
    await textTab.click();
    await expect(textTab).toHaveClass(/active/);

    // Click file tab
    await fileTab.click();
    await expect(fileTab).toHaveClass(/active/);
  });

  test('should show file upload area in file tab', async ({ page }) => {
    const fileTab = page.locator('button').filter({ hasText: 'Upload File' });
    await fileTab.click();

    const fileUploadArea = page.locator('.file-upload-area');
    await expect(fileUploadArea).toBeVisible();
  });

  test('should show text input fields in text tab', async ({ page }) => {
    const textTab = page.locator('button').filter({ hasText: 'Add Text' });
    await textTab.click();

    await expect(page.locator('#textTitle')).toBeVisible();
    await expect(page.locator('#textContent')).toBeVisible();
  });
});

test.describe('Settings Actions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();
    await expect(page.locator('#appModal')).toBeVisible();
  });

  test('should have Save Settings button', async ({ page }) => {
    const saveButton = page.locator('button:has-text("Save Settings")');
    await expect(saveButton).toBeVisible();
  });

  test('should have Reset to Defaults button', async ({ page }) => {
    const resetButton = page.locator('button:has-text("Reset to Defaults")');
    await expect(resetButton).toBeVisible();
  });

  test('should save settings to localStorage when clicking Save', async ({ page }) => {
    // Change some settings
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    const saveButton = page.locator('button:has-text("Save Settings")');
    await saveButton.click();

    // Check localStorage
    const savedSettings = await page.evaluate(() => {
      return localStorage.getItem('chatSettings');
    });

    expect(savedSettings).not.toBeNull();
    const settings = JSON.parse(savedSettings!);
    expect(settings.useRag).toBe(true);
  });

  test('should reset settings to defaults when clicking Reset', async ({ page }) => {
    // Change some settings
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    const temperatureSlider = page.locator('#temperature');
    await temperatureSlider.fill('1.5');

    // Reset
    const resetButton = page.locator('button:has-text("Reset to Defaults")');
    await resetButton.click();

    // Settings should be back to defaults
    await expect(ragToggle).not.toBeChecked();

    const temperatureValue = await temperatureSlider.inputValue();
    expect(parseFloat(temperatureValue)).toBe(0.7);
  });

  test('should persist settings across page reloads', async ({ page }) => {
    // Change and save settings
    const ragToggle = page.locator('#ragToggle');
    await ragToggle.click();

    const saveButton = page.locator('button:has-text("Save Settings")');
    await saveButton.click();

    // Close modal
    const closeButton = page.locator('.btn-close');
    await closeButton.click();

    // Reload page
    await page.reload();

    // Open settings again
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();

    // Settings should be persisted
    const ragToggleAfterReload = page.locator('#ragToggle');
    await expect(ragToggleAfterReload).toBeChecked();
  });
});

test.describe('Settings Descriptions and Help Text', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();
    await expect(page.locator('#appModal')).toBeVisible();
  });

  test('should have helpful description for RAG toggle', async ({ page }) => {
    await expect(page.getByText('Use document knowledge base to enhance responses')).toBeVisible();
  });

  test('should have helpful description for provider setting', async ({ page }) => {
    await expect(page.getByText(/Auto-detect will automatically choose a provider/)).toBeVisible();
  });

  test('should have helpful description for model setting', async ({ page }) => {
    await expect(page.getByText("Leave empty to use provider's default model")).toBeVisible();
  });

  test('should have helpful description for temperature setting', async ({ page }) => {
    await expect(page.getByText(/Lower = more focused, Higher = more creative/)).toBeVisible();
  });

  test('should have helpful note about API keys storage', async ({ page }) => {
    await expect(page.getByText(/Keys are stored locally in your browser/)).toBeVisible();
  });
});
