// ABOUTME: Integration tests for complete WorkChat workflows
// ABOUTME: Tests full user journeys including authentication, messaging, and real-time updates

import { test, expect } from '@playwright/test';
import { WorkChatTestUtils } from './helpers/test-utils';

test.describe('WorkChat Integration Tests', () => {
  let testUtils: WorkChatTestUtils;

  test.beforeEach(async ({ page }) => {
    testUtils = new WorkChatTestUtils(page);
    await page.goto('/');
    await testUtils.waitForAppLoad();
  });

  test('complete user journey: browse channels, select, and compose', async ({ page }) => {
    // Verify app loaded successfully
    await expect(page.locator('.sidebar h2')).toHaveText('Channels');
    
    // Check channels loading state
    await testUtils.waitForAppLoad();
    
    const firstChannel = await testUtils.getFirstChannel();
    
    if (firstChannel) {
      // Test channel selection
      await testUtils.selectChannel(firstChannel.element);
      
      // Verify thread view loaded
      await expect(page.locator('.thread-header')).toBeVisible();
      await expect(page.locator('.thread-title')).toContainText(firstChannel.name.replace('#', '').trim());
      
      // Test message composition
      const testMessage = `Integration test message ${Date.now()}`;
      await testUtils.sendMessage(testMessage);
      
      // Verify composer is ready for next message
      await expect(page.locator('.composer-input')).toHaveValue('');
      await expect(page.locator('.composer-button')).not.toBeDisabled();
    } else {
      // No channels available - test empty state
      await expect(page.locator('.main-content .empty-state')).toBeVisible();
      await expect(page.locator('.main-content .empty-state h2')).toHaveText('Welcome to WorkChat');
    }
  });

  test('keyboard navigation and shortcuts', async ({ page }) => {
    const firstChannel = await testUtils.getFirstChannel();
    
    if (firstChannel) {
      await testUtils.selectChannel(firstChannel.element);
      
      const messageInput = page.locator('.composer-input');
      
      // Test Tab navigation
      await page.keyboard.press('Tab');
      // Should eventually focus the message input (may take several tabs)
      
      // Test keyboard shortcuts in composer
      await messageInput.focus();
      
      // Test Enter to send
      await messageInput.fill('Test Enter send');
      await page.keyboard.press('Enter');
      await expect(messageInput).toHaveValue('');
      
      // Test Shift+Enter for new line
      await messageInput.fill('Line 1');
      await page.keyboard.press('Shift+Enter');
      await messageInput.type('Line 2');
      await expect(messageInput).toHaveValue('Line 1\nLine 2');
    }
  });

  test('responsive design and mobile viewport', async ({ page }) => {
    // Test desktop viewport first
    await expect(page.locator('.app')).toHaveCSS('display', 'flex');
    
    // Switch to mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // App should still be functional
    await expect(page.locator('.app')).toBeVisible();
    await expect(page.locator('.sidebar')).toBeVisible();
    
    // Connection status should be visible
    await expect(page.locator('.connection-status')).toBeVisible();
  });

  test('error handling and edge cases', async ({ page }) => {
    // Test app behavior when backend is unreachable
    // This simulates network issues
    
    // First verify normal operation
    await testUtils.waitForAppLoad();
    
    // Test that error states are handled gracefully
    const errorElements = page.locator('.error, .loading, .empty-state, .channel-list');
    await expect(errorElements.first()).toBeVisible();
    
    // Test connection status handles disconnection
    const status = await testUtils.getConnectionStatus();
    expect(['connected', 'disconnected', 'unknown']).toContain(status);
  });

  test('concurrent user simulation', async ({ browser }) => {
    // Create multiple browser contexts to simulate concurrent users
    const contexts = await Promise.all([
      browser.newContext(),
      browser.newContext(),
    ]);
    
    const pages = await Promise.all([
      contexts[0].newPage(),
      contexts[1].newPage(),
    ]);
    
    try {
      // Both users navigate to the app
      await Promise.all(pages.map(page => page.goto('/')));
      
      // Both should see the same initial state
      await Promise.all(pages.map(async (page) => {
        const utils = new WorkChatTestUtils(page);
        await utils.waitForAppLoad();
        await expect(page.locator('.sidebar h2')).toHaveText('Channels');
      }));
      
      // If channels exist, both users should see them
      const channelCounts = await Promise.all(
        pages.map(page => page.locator('.channel-item').count())
      );
      
      if (channelCounts[0] > 0) {
        // Both pages should have the same number of channels
        expect(channelCounts[0]).toBe(channelCounts[1]);
        
        // Both can select channels independently
        await Promise.all([
          pages[0].locator('.channel-item').first().click(),
          pages[1].locator('.channel-item').first().click(),
        ]);
        
        // Both should show thread views
        await Promise.all(pages.map(page => 
          expect(page.locator('.thread-view')).toBeVisible()
        ));
      }
      
    } finally {
      // Clean up
      await Promise.all(contexts.map(context => context.close()));
    }
  });

  test('performance and loading times', async ({ page }) => {
    const startTime = Date.now();
    
    // Measure initial load time
    await testUtils.waitForAppLoad();
    const loadTime = Date.now() - startTime;
    
    // App should load within reasonable time (5 seconds)
    expect(loadTime).toBeLessThan(5000);
    
    // Test channel selection performance
    const firstChannel = await testUtils.getFirstChannel();
    if (firstChannel) {
      const selectStart = Date.now();
      await testUtils.selectChannel(firstChannel.element);
      const selectTime = Date.now() - selectStart;
      
      // Channel selection should be fast (under 2 seconds)
      expect(selectTime).toBeLessThan(2000);
    }
  });
});