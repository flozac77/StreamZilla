describe('Search Feature', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should show search bar centered on page load', () => {
    cy.get('input[type="text"]')
      .should('be.visible')
      .should('have.css', 'transform', 'none')
  })

  it('should move search bar up when searching', () => {
    cy.get('input[type="text"]')
      .type('Minecraft{enter}')
      .should('have.css', 'transform')
      .and('not.equal', 'none')
  })

  it('should show loading state when searching', () => {
    cy.get('input[type="text"]').type('Minecraft{enter}')
    cy.get('.animate-spin').should('be.visible')
  })

  it('should display video results after search', () => {
    cy.intercept('GET', '/api/twitch/search*', {
      fixture: 'searchResults.json'
    }).as('searchRequest')

    cy.get('input[type="text"]').type('Minecraft{enter}')
    cy.wait('@searchRequest')
    cy.get('[data-testid="video-card"]').should('have.length.gt', 0)
  })

  it('should show error message when API fails', () => {
    cy.intercept('GET', '/api/twitch/search*', {
      statusCode: 500,
      body: {
        detail: 'Une erreur est survenue'
      }
    }).as('failedRequest')

    cy.get('input[type="text"]').type('Minecraft{enter}')
    cy.wait('@failedRequest')
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .and('contain', 'Une erreur est survenue')
  })

  it('should load more videos on scroll', () => {
    cy.intercept('GET', '/api/twitch/search*', {
      fixture: 'searchResults.json'
    }).as('searchRequest')

    cy.get('input[type="text"]').type('Minecraft{enter}')
    cy.wait('@searchRequest')
    cy.scrollTo('bottom')
    cy.get('[data-testid="video-card"]').should('have.length.gt', 10)
  })
}) 