import { test as base, Page } from '@playwright/test';

/**
 * Custom fixture types for the chat application
 */
type ChatFixtures = {
  authenticatedPage: Page;
  settingsModal: Page;
};

/**
 * Helper functions for common test operations
 */
export const helpers = {
  /**
   * Simulate user login by setting localStorage
   */
  async loginUser(page: Page, username: string = 'testuser', token: string = 'fake-token') {
    await page.evaluate(
      ({ username, token }) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify({ username }));
      },
      { username, token }
    );
    await page.reload();
  },

  /**
   * Clear authentication state
   */
  async logout(page: Page) {
    await page.evaluate(() => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    });
    await page.reload();
  },

  /**
   * Open the settings modal
   */
  async openSettings(page: Page) {
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();
    await page.waitForSelector('#appModal.show', { timeout: 5000 });
  },

  /**
   * Close any open modal
   */
  async closeModal(page: Page) {
    const closeButton = page.locator('.btn-close');
    await closeButton.click();
    await page.waitForTimeout(500); // Wait for modal close animation
  },

  /**
   * Send a chat message
   */
  async sendMessage(page: Page, message: string) {
    const inputField = page.locator('.input-field');
    await inputField.fill(message);
    await inputField.press('Enter');
  },

  /**
   * Wait for chat response to complete
   */
  async waitForChatResponse(page: Page, timeout: number = 10000) {
    // Wait for loading indicator to disappear
    await page.waitForSelector('.typing-indicator', { state: 'hidden', timeout });
  },

  /**
   * Enable RAG mode
   */
  async enableRagMode(page: Page, topK: number = 5, minScore: number = 0.3) {
    await helpers.openSettings(page);

    const ragToggle = page.locator('#ragToggle');
    const isChecked = await ragToggle.isChecked();
    if (!isChecked) {
      await ragToggle.click();
    }

    if (topK !== 5) {
      const topKSlider = page.locator('#topK');
      await topKSlider.fill(topK.toString());
    }

    if (minScore !== 0.3) {
      const minScoreSlider = page.locator('#minScore');
      await minScoreSlider.fill(minScore.toString());
    }

    const saveButton = page.locator('button:has-text("Save Settings")');
    await saveButton.click();

    await helpers.closeModal(page);
  },

  /**
   * Set API key for a provider
   */
  async setApiKey(page: Page, provider: 'gemini' | 'openai' | 'anthropic', apiKey: string) {
    await helpers.openSettings(page);

    const inputMap = {
      gemini: '#geminiApiKey',
      openai: '#openaiApiKey',
      anthropic: '#anthropicApiKey',
    };

    const input = page.locator(inputMap[provider]);
    await input.fill(apiKey);

    const saveButton = page.locator('button:has-text("Save Settings")');
    await saveButton.click();

    await helpers.closeModal(page);
  },

  /**
   * Get all messages from the chat
   */
  async getChatMessages(page: Page): Promise<Array<{ text: string; sender: 'user' | 'bot' }>> {
    const messages = await page.locator('.message-group').all();
    const result = [];

    for (const message of messages) {
      const classes = await message.getAttribute('class');
      const sender = classes?.includes('user') ? 'user' : 'bot';
      const text = await message.locator('.message-bubble').textContent();
      result.push({ text: text || '', sender });
    }

    return result;
  },

  /**
   * Toggle sidebar visibility
   */
  async toggleSidebar(page: Page) {
    const menuButton = page.locator('.menu-btn');
    await menuButton.click();
  },

  /**
   * Create a new chat
   */
  async createNewChat(page: Page) {
    const newChatButton = page.locator('.new-chat-btn');
    await newChatButton.click();
  },

  /**
   * Clear all localStorage data
   */
  async clearStorage(page: Page) {
    await page.evaluate(() => localStorage.clear());
  },

  /**
   * Set chat settings in localStorage
   */
  async setChatSettings(page: Page, settings: Partial<any>) {
    await page.evaluate((settings) => {
      const defaultSettings = {
        useRag: false,
        topK: 5,
        minScore: 0.3,
        provider: '',
        model: '',
        temperature: 0.7,
        geminiApiKey: '',
        openaiApiKey: '',
        anthropicApiKey: '',
      };
      const merged = { ...defaultSettings, ...settings };
      localStorage.setItem('chatSettings', JSON.stringify(merged));
    }, settings);
    await page.reload();
  },

  /**
   * Get chat settings from localStorage
   */
  async getChatSettings(page: Page): Promise<any> {
    return await page.evaluate(() => {
      const settings = localStorage.getItem('chatSettings');
      return settings ? JSON.parse(settings) : null;
    });
  },

  /**
   * Mock API response
   */
  async mockApiResponse(
    page: Page,
    url: string | RegExp,
    response: any,
    status: number = 200
  ) {
    await page.route(url, async (route) => {
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(response),
      });
    });
  },

  /**
   * Wait for an element to be visible with custom timeout
   */
  async waitForElement(page: Page, selector: string, timeout: number = 5000) {
    await page.waitForSelector(selector, { state: 'visible', timeout });
  },

  /**
   * Check if an element exists (returns boolean)
   */
  async elementExists(page: Page, selector: string): Promise<boolean> {
    const count = await page.locator(selector).count();
    return count > 0;
  },

  /**
   * Scroll to bottom of messages
   */
  async scrollToBottom(page: Page) {
    await page.evaluate(() => {
      const endOfMessages = document.querySelector('.messages-container');
      if (endOfMessages) {
        endOfMessages.scrollTop = endOfMessages.scrollHeight;
      }
    });
  },
};

/**
 * Extended test with custom fixtures
 */
export const test = base.extend<ChatFixtures>({
  /**
   * Fixture that provides an authenticated page
   */
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/');
    await helpers.loginUser(page);
    await use(page);
  },

  /**
   * Fixture that provides a page with settings modal open
   */
  settingsModal: async ({ page }, use) => {
    await page.goto('/');
    await helpers.openSettings(page);
    await use(page);
  },
});

export { expect } from '@playwright/test';
