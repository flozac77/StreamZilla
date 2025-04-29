import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/videos/:game',
      name: 'videos',
      component: () => import('../views/VideoListView.vue')
    },
    {
      path: '/search/:game',
      redirect: to => {
        // Redirige /search/fortnite vers /videos/fortnite
        return { path: `/videos/${to.params.game}` }
      }
    }
  ]
})

export default router 