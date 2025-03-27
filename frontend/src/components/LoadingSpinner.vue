<template>
  <div class="flex flex-col items-center justify-center h-64">
    <div class="relative">
      <!-- Spinner principal -->
      <div class="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
      
      <!-- Overlay avec texte -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="w-8 h-8 bg-white dark:bg-gray-800 rounded-full"></div>
      </div>
    </div>
    
    <!-- Message de chargement -->
    <p class="mt-4 text-gray-600 dark:text-gray-300 text-sm animate-pulse">
      {{ message || 'Chargement en cours...' }}
    </p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message?: string
}>()
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style> 