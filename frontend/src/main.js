import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import axios from 'axios'
import VueLazyload from 'vue-lazyload'
import './assets/main.css'

// Configuration d'Axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const app = createApp(App)
const pinia = createPinia()

// Installation des plugins
app.use(pinia)
app.use(VueLazyload, {
  preLoad: 1.3,
  error: '/error-image.png',
  loading: '/loading-image.gif',
  attempt: 1
})

app.mount('#app') 