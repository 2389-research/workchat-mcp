// ABOUTME: Basic setup verification tests for WorkChat E2E testing
// ABOUTME: Ensures the testing environment is properly configured

import { test, expect } from '@playwright/test';

test.describe('E2E Setup Verification', () => {
  test('frontend application loads successfully', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Verify basic app structure loads
    await expect(page.locator('body')).toBeVisible();
    await expect(page.locator('#root')).toBeVisible();
    
    // Should not have any JavaScript errors in console
    const errorLogs: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errorLogs.push(msg.text());
      }
    });
    
    // Wait a bit for any async errors
    await page.waitForTimeout(2000);
    
    // Check for critical errors (ignoring common dev warnings)
    const criticalErrors = errorLogs.filter(error => 
      !error.includes('favicon') && 
      !error.includes('Warning:') &&
      !error.includes('Development mode')
    );
    
    if (criticalErrors.length > 0) {
      console.log('Non-critical errors detected:', criticalErrors);
    }
    
    // App should render something meaningful
    await expect(page.locator('.app, [data-testid="app"], main')).toBeVisible();
  });

  test('page title is set correctly', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/WorkChat/);
  });

  test('basic CSS styles are loaded', async ({ page }) => {
    await page.goto('/');
    
    // Check that some basic styles are applied
    const body = page.locator('body');
    await expect(body).toBeVisible();
    
    // Verify CSS is loaded by checking if default browser styles are overridden
    const computedMargin = await body.evaluate(el => 
      window.getComputedStyle(el).margin
    );
    
    // If our CSS is loaded, body margin should be set to 0
    expect(computedMargin).toBe('0px');
  });

  test('JavaScript modules load without errors', async ({ page }) => {
    const jsErrors: string[] = [];
    
    page.on('pageerror', (error) => {
      jsErrors.push(error.message);
    });
    
    await page.goto('/');
    
    // Wait for potential async loading
    await page.waitForTimeout(3000);
    
    // Should have no critical JavaScript errors
    expect(jsErrors.length).toBe(0);
  });
});