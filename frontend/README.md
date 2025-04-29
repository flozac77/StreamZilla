# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

# Twitch Video Search Frontend

[![Tests](https://github.com/flozac77/StreamZilla/actions/workflows/test.yml/badge.svg)](https://github.com/flozac77/StreamZilla/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/flozac77/StreamZilla/branch/main/graph/badge.svg)](https://codecov.io/gh/flozac77/StreamZilla)

## Tests

### Tests Unitaires
```bash
npm run test:unit         # Lance les tests une fois
npm run test:unit:watch   # Lance les tests en mode watch
npm run test:unit:coverage # Lance les tests avec couverture
```

### Tests E2E
```bash
npm run test:e2e         # Lance tous les tests E2E
npm run test:e2e -- --ui # Lance l'interface utilisateur de Playwright
```

## Couverture de Code

La couverture de code est générée automatiquement lors de l'exécution des tests unitaires avec l'option `--coverage`. Les rapports sont disponibles dans le dossier `coverage/`.
