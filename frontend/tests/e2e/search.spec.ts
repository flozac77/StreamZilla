import { test, expect } from '@playwright/test'

test.describe('Video Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display search bar', async ({ page }) => {
    await expect(page.getByPlaceholder('Search for a game...')).toBeVisible()
  })

  test('should display filters', async ({ page }) => {
    await expect(page.getByTestId('date-filter')).toBeVisible()
    await expect(page.getByTestId('duration-filter')).toBeVisible()
    await expect(page.getByTestId('views-filter')).toBeVisible()
    await expect(page.getByTestId('language-filter')).toBeVisible()
  })

  test('should perform a search', async ({ page }) => {
    const searchInput = page.getByPlaceholder('Search for a game...')
    await searchInput.fill('Minecraft')
    await searchInput.press('Enter')
    
    // Wait for results to display
    await expect(page.getByTestId('video-grid')).toBeVisible()
    
    // Check that at least one video is displayed
    const videos = page.getByTestId('video-card')
    await expect(videos.first()).toBeVisible()
  })

  test('should filter results', async ({ page }) => {
    // Perform a search
    const searchInput = page.getByPlaceholder('Search for a game...')
    await searchInput.fill('Minecraft')
    await searchInput.press('Enter')

    // Apply a date filter
    await page.getByTestId('date-today').click()
    
    // Check that the filter is applied
    await expect(page.getByTestId('date-today')).toHaveClass(/active/)
    
    // Check that the grid is updated
    await expect(page.getByTestId('video-grid')).toBeVisible()
  })
}) 