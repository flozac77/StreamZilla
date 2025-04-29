import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Toast from 'vue-toastification'
import VueLazyload from 'vue-lazyload'
import 'vue-toastification/dist/index.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Toast, {
  transition: 'Vue-Toastification__bounce',
  maxToasts: 3,
  newestOnTop: true
})
app.use(VueLazyload, {
  preLoad: 1.3,
  error: '/error.png',
  loading: '/loading.gif',
  attempt: 1
})

app.mount('#app')
