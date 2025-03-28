/// <reference types="vitest" />
import { defineConfig } from 'vite'
import Vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [Vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
    include: ['tests/**/*.spec.ts'],
    deps: {
      inline: ['@vue', '@vueuse', 'pinia']
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
}) 