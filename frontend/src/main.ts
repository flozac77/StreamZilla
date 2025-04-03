import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Toast from 'vue-toastification'
import VueLazyload from 'vue-lazyload'
import axios from 'axios'
import 'vue-toastification/dist/index.css'

// Configuration d'Axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const app = createApp(App)
const pinia = createPinia()

// Configuration des plugins
app.use(pinia)
app.use(router)
app.use(Toast, {
  position: 'top-right',
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: true,
  closeButton: 'button',
  icon: true,
  rtl: false
})
app.use(VueLazyload, {
  preLoad: 1.3,
  error: '/error-image.png',
  loading: '/loading-image.gif',
  attempt: 1
})

app.mount('#app')
