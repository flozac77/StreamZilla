describe('Video Search', () => {
  beforeEach(() => {
    // Intercepter les appels API
    cy.intercept('GET', '**/api/search**', { fixture: 'searchResults.json' }).as('searchVideos')
    cy.visit('/')
  })

  it('should search for videos and apply filters', () => {
    // Test de la recherche
    cy.get('[data-test="search-input"]').type('Minecraft')
    cy.get('[data-test="search-button"]').click()
    cy.wait('@searchVideos')

    // Vérifier que les vidéos sont affichées
    cy.get('[data-test="video-card"]').should('have.length.at.least', 1)

    // Test des filtres
    cy.get('select[data-test="date-filter"]').select('today')
    cy.get('select[data-test="duration-filter"]').select('short')
    cy.get('select[data-test="views-filter"]').select('less_100')
    cy.get('select[data-test="language-filter"]').select('fr')

    // Vérifier que les filtres sont appliqués
    cy.get('[data-test="video-card"]').should('exist')

    // Test du tri
    cy.get('[data-test="sort-views"]').click()
    cy.get('[data-test="video-card"]').first().should('contain', 'vues')
  })

  it('should handle search with no results', () => {
    // Intercepter avec une réponse vide
    cy.intercept('GET', '**/api/search**', {
      statusCode: 200,
      body: {
        videos: [],
        game: null,
        total_count: 0
      }
    }).as('emptySearch')

    cy.get('[data-test="search-input"]').type('JeuInexistant')
    cy.get('[data-test="search-button"]').click()
    cy.wait('@emptySearch')

    // Vérifier le message d'absence de résultats
    cy.get('[data-test="no-results"]').should('be.visible')
  })

  it('should handle API errors gracefully', () => {
    // Intercepter avec une erreur
    cy.intercept('GET', '**/api/search**', {
      statusCode: 500,
      body: {
        detail: 'Internal Server Error'
      }
    }).as('errorSearch')

    cy.get('[data-test="search-input"]').type('Minecraft')
    cy.get('[data-test="search-button"]').click()
    cy.wait('@errorSearch')

    // Vérifier le message d'erreur
    cy.get('[data-test="error-message"]').should('be.visible')
  })

  it('should load more videos on scroll', () => {
    cy.get('[data-test="search-input"]').type('Minecraft')
    cy.get('[data-test="search-button"]').click()
    cy.wait('@searchVideos')

    // Vérifier le nombre initial de vidéos
    cy.get('[data-test="video-card"]').should('have.length.at.least', 1)

    // Intercepter le chargement de plus de vidéos
    cy.intercept('GET', '**/api/search**', { fixture: 'moreVideos.json' }).as('loadMore')

    // Scroll jusqu'en bas
    cy.scrollTo('bottom')
    cy.wait('@loadMore')

    // Vérifier qu'il y a plus de vidéos
    cy.get('[data-test="video-card"]').should('have.length.gt', 12)
  })

  it('should persist filters in URL', () => {
    // Appliquer des filtres
    cy.get('select[data-test="date-filter"]').select('today')
    cy.get('select[data-test="duration-filter"]').select('short')

    // Vérifier que l'URL contient les paramètres
    cy.url().should('include', 'date=today')
    cy.url().should('include', 'duration=short')

    // Recharger la page
    cy.reload()

    // Vérifier que les filtres sont toujours appliqués
    cy.get('select[data-test="date-filter"]').should('have.value', 'today')
    cy.get('select[data-test="duration-filter"]').should('have.value', 'short')
  })
}) 