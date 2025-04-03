import { test, expect } from '@playwright/test'

test.describe('Recherche de vidéos', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('doit afficher la barre de recherche', async ({ page }) => {
    await expect(page.getByPlaceholder('Rechercher un jeu...')).toBeVisible()
  })

  test('doit afficher les filtres', async ({ page }) => {
    await expect(page.getByTestId('date-filter')).toBeVisible()
    await expect(page.getByTestId('duration-filter')).toBeVisible()
    await expect(page.getByTestId('views-filter')).toBeVisible()
    await expect(page.getByTestId('language-filter')).toBeVisible()
  })

  test('doit effectuer une recherche', async ({ page }) => {
    const searchInput = page.getByPlaceholder('Rechercher un jeu...')
    await searchInput.fill('Minecraft')
    await searchInput.press('Enter')
    
    // Attendre que les résultats s'affichent
    await expect(page.getByTestId('video-grid')).toBeVisible()
    
    // Vérifier qu'au moins une vidéo est affichée
    const videos = page.getByTestId('video-card')
    await expect(videos.first()).toBeVisible()
  })

  test('doit filtrer les résultats', async ({ page }) => {
    // Effectuer une recherche
    const searchInput = page.getByPlaceholder('Rechercher un jeu...')
    await searchInput.fill('Minecraft')
    await searchInput.press('Enter')

    // Appliquer un filtre de date
    await page.getByTestId('date-today').click()
    
    // Vérifier que le filtre est appliqué
    await expect(page.getByTestId('date-today')).toHaveClass(/active/)
    
    // Vérifier que la grille est mise à jour
    await expect(page.getByTestId('video-grid')).toBeVisible()
  })
}) 