import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import prettierConfig from '@vue/eslint-config-prettier'

export default [
  {
    name: 'app/files-to-lint',
    files: ['**/*.{js,mjs,jsx,vue}'],
  },

  {
    name: 'app/files-to-ignore',
    ignores: [
      '**/dist/**',
      '**/dist-ssr/**',
      '**/coverage/**',
      '**/node_modules/**',
      '**/auto-imports.d.ts',
      '**/components.d.ts',
      '**/src/types/**',
    ],
  },

  js.configs.recommended,
  ...pluginVue.configs['flat/essential'],
  prettierConfig,

  {
    name: 'app/browser-globals',
    languageOptions: {
      globals: {
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        navigator: 'readonly',
        console: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        FormData: 'readonly',
        fetch: 'readonly',
        Blob: 'readonly',
        URL: 'readonly',
        // Node.js globals for config files
        process: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        global: 'readonly',
      },
    },
  },

  {
    name: 'app/vue-rules',
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: '@babel/eslint-parser',
        requireConfigFile: false,
        sourceType: 'module',
        babelOptions: {
          presets: ['@babel/preset-env'],
        },
      },
    },
    rules: {
      // Vue特定规则
      'vue/multi-word-component-names': 'off',
      'vue/no-unused-vars': 'error',
      'vue/no-unused-components': 'warn',
      'vue/require-v-for-key': 'error',
      'vue/no-use-v-if-with-v-for': 'error',
    },
  },

  {
    name: 'app/javascript-rules',
    files: ['**/*.{js,mjs,jsx}'],
    rules: {
      // JavaScript通用规则
      'no-console': 'off', // 允许console，由logger工具管理
      'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'prefer-const': 'error',
      'no-var': 'error',
      'object-shorthand': 'error',
      'prefer-template': 'error',
      'no-prototype-builtins': 'error',
    },
  },

  {
    name: 'app/test-files',
    files: ['tests/**/*.{js,mjs}', '**/*.test.{js,mjs}', '**/*.spec.{js,mjs}'],
    rules: {
      'no-console': 'off',
      'no-unused-vars': 'off',
    },
  },
]
