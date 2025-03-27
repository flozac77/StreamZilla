import { defineStore } from 'pinia'

interface SearchHistoryItem {
  query: string
  timestamp: number
}

export const useUserPreferencesStore = defineStore('userPreferences', {
  state: () => ({
    searchHistory: [] as SearchHistoryItem[],
    favoriteGames: [] as string[],
    maxHistoryItems: 10
  }),

  actions: {
    addToHistory(query: string) {
      // Supprimer les doublons
      this.searchHistory = this.searchHistory.filter(item => item.query !== query)
      
      // Ajouter la nouvelle recherche
      this.searchHistory.unshift({
        query,
        timestamp: Date.now()
      })

      // Limiter la taille de l'historique
      if (this.searchHistory.length > this.maxHistoryItems) {
        this.searchHistory = this.searchHistory.slice(0, this.maxHistoryItems)
      }

      // Sauvegarder dans le localStorage
      this.saveToLocalStorage()
    },

    clearHistory() {
      this.searchHistory = []
      this.saveToLocalStorage()
    },

    toggleFavorite(game: string) {
      const index = this.favoriteGames.indexOf(game)
      if (index === -1) {
        this.favoriteGames.push(game)
      } else {
        this.favoriteGames.splice(index, 1)
      }
      this.saveToLocalStorage()
    },

    isFavorite(game: string): boolean {
      return this.favoriteGames.includes(game)
    },

    loadFromLocalStorage() {
      try {
        const history = localStorage.getItem('searchHistory')
        const favorites = localStorage.getItem('favoriteGames')
        
        if (history) {
          this.searchHistory = JSON.parse(history)
        }
        
        if (favorites) {
          this.favoriteGames = JSON.parse(favorites)
        }
      } catch (e) {
        console.error('Erreur lors du chargement des préférences:', e)
      }
    },

    saveToLocalStorage() {
      try {
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
        localStorage.setItem('favoriteGames', JSON.stringify(this.favoriteGames))
      } catch (e) {
        console.error('Erreur lors de la sauvegarde des préférences:', e)
      }
    }
  }
}) 