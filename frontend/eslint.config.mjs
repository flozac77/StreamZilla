import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";
import pluginVue from "eslint-plugin-vue";
import unusedImports from "eslint-plugin-unused-imports";
import vitestPlugin from "eslint-plugin-vitest";

export default [
  { languageOptions: { globals: { ...globals.browser, ...globals.node } } }, // Added node globals for config files
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs["flat/essential"], 
  { // Vue specific parser configuration
    files: ["**/*.vue"],
    languageOptions: { 
      parserOptions: { 
        parser: tseslint.parser 
      } 
    },
    rules: {
      // Add any Vue specific rule overrides here if needed
    }
  },
  { // General rules for TS and JS files, including unused imports
    plugins: {
      "unused-imports": unusedImports,
      // "@typescript-eslint": tseslint.plugin, // tseslint.plugin is not how it's typically structured for flat config
    },
    rules: {
      "no-unused-vars": "off", // Off because @typescript-eslint/no-unused-vars is used
      "@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_", "varsIgnorePattern": "^_" }],
      "unused-imports/no-unused-imports": "warn",
      // The rule below is redundant if @typescript-eslint/no-unused-vars is active and configured
      // "unused-imports/no-unused-vars": [ 
      //   "warn",
      //   { "vars": "all", "varsIgnorePattern": "^_", "args": "after-used", "argsIgnorePattern": "^_" }
      // ],
      "@typescript-eslint/no-explicit-any": "warn", // Changed from error to warn for now
      "@typescript-eslint/no-empty-object-type": "warn", // Changed from error to warn
    }
  },
  { // Vitest specific configuration for .ts/.vue test files
    files: ["**/*.{test,spec}.{ts,mts,cts}", "**/*.spec.vue"], // More specific to TS/Vue for Vitest plugin
    plugins: {
        vitest: vitestPlugin,
    },
    rules: {
        ...vitestPlugin.configs.recommended.rules,
    },
    languageOptions: {
        globals: {
            ...globals.vitest,
        },
    },
  },
  { // Jest specific globals for older .spec.js files
    files: ["**/*.spec.js"],
    languageOptions: {
        globals: {
            ...globals.jest,
        },
    },
  },
  {
    // Ignores generated files or specific directories
    ignores: ["dist/", "node_modules/", "cypress/", "playwright-report/", "tests/e2e/", "**/*.d.ts"]
  }
];
