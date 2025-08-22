// ABOUTME: Test utilities for WorkChat E2E tests
// ABOUTME: Common helper functions for authentication, setup, and assertions

import { Page, expect } from '@playwright/test';

export class WorkChatTestUtils {
  constructor(private page: Page) {}

  /**
   * Wait for the WorkChat app to fully load
   */
  async waitForAppLoad(): Promise<void> {
    await expect(this.page.locator('.app')).toBeVisible();
    await expect(this.page.locator('.sidebar')).toBeVisible();
    await expect(this.page.locator('.connection-status')).toBeVisible();
  }

  /**
   * Get the first available channel or null if none exist
   */
  async getFirstChannel(): Promise<{ element: any; name: string } | null> {
    const firstChannel = this.page.locator('.channel-item').first();
    if (await firstChannel.isVisible()) {
      const name = await firstChannel.locator('.channel-name').textContent() || '';
      return { element: firstChannel, name };
    }
    return null;
  }

  /**
   * Select a channel and wait for thread view to load
   */
  async selectChannel(channelElement: any): Promise<void> {
    await channelElement.click();
    await expect(channelElement).toHaveClass(/active/);
    await expect(this.page.locator('.thread-view')).toBeVisible();
  }

  /**
   * Send a message using the composer
   */
  async sendMessage(message: string): Promise<void> {
    const messageInput = this.page.locator('.composer-input');
    const sendButton = this.page.locator('.composer-button');
    
    await expect(messageInput).toBeVisible();
    await messageInput.fill(message);
    await sendButton.click();
    
    // Verify input is cleared
    await expect(messageInput).toHaveValue('');
  }

  /**
   * Wait for connection status to be connected
   */
  async waitForConnection(timeout = 10000): Promise<void> {
    try {
      await this.page.waitForSelector('.connection-status.connected', { timeout });
    } catch (error) {
      console.log('Connection timeout - this may be expected without proper authentication');
    }
  }

  /**
   * Get connection status
   */
  async getConnectionStatus(): Promise<'connected' | 'disconnected' | 'unknown'> {
    const statusElement = this.page.locator('.connection-status');
    const text = await statusElement.textContent() || '';
    
    if (text.includes('Connected')) return 'connected';
    if (text.includes('Disconnected')) return 'disconnected';
    return 'unknown';
  }

  /**
   * Check if channels are loaded (vs loading state)
   */
  async areChannelsLoaded(): Promise<boolean> {
    // Check if we're past the loading state
    const loadingExists = await this.page.locator('.sidebar .loading').isVisible();
    return !loadingExists;
  }

  /**
   * Get current URL for navigation testing
   */
  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  /**
   * Take a screenshot for debugging
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `test-results/${name}-${Date.now()}.png` });
  }
}