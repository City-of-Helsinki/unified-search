import js from '@eslint/js';
import stylisticPlugin from '@stylistic/eslint-plugin';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import importPlugin from 'eslint-plugin-import';
import nPlugin from 'eslint-plugin-n';
import prettierPlugin from 'eslint-plugin-prettier';
import promisePlugin from 'eslint-plugin-promise';
import globals from 'globals';

const files = ['**/*.js', '**/*.ts', '**/*.cjs', '**/*.mjs'];

export default [
  // Ignores
  {
    ignores: [
      '**/.cache/',
      '**/.config/',
      '**/build/',
      '**/coverage/',
      '**/dist/',
      '**/generated-graphql-docs/**',
      '**/node_modules/',
    ],
  },

  // import config
  {
    files,
    plugins: { import: importPlugin },
    rules: {
      ...importPlugin.flatConfigs.recommended.rules,
      'import/order': [
        'error',
        {
          groups: [
            'builtin',
            'external',
            ['internal', 'parent', 'sibling', 'index'],
          ],
          'newlines-between': 'always',
          alphabetize: {
            order: 'asc',
            caseInsensitive: true,
          },
        },
      ],
    },
  },

  // Stylistic rules
  {
    files,
    plugins: { '@stylistic': stylisticPlugin },
    rules: {
      '@stylistic/brace-style': ['error', '1tbs', { allowSingleLine: true }],
      'array-bracket-spacing': ['warn', 'never'],
      'object-curly-spacing': ['warn', 'always'],
    },
  },

  // prettier config
  {
    files,
    plugins: { prettier: prettierPlugin },
    rules: {
      'prettier/prettier': 'error',
      // Turn off rules that may cause problems, see
      // https://github.com/prettier/eslint-plugin-prettier/issues/65
      'arrow-body-style': 'off',
      'prefer-arrow-callback': 'off',
    },
  },

  // General rules
  {
    files,
    languageOptions: {
      parser: tsParser,
      globals: {
        ...globals.node,
      },
    },
    settings: {
      'import/resolver': {
        typescript: {
          alwaysTryTypes: true,
          project: './tsconfig.json',
        },
      },
    },
    linterOptions: {
      reportUnusedDisableDirectives: true,
    },
    rules: {
      ...js.configs.recommended.rules,
      'max-len': ['warn', { code: 120, ignoreUrls: true }],
      'no-console': 'warn',
      'no-plusplus': 'error',
      'no-undef': 'warn',
    },
  },

  // n(ode) plugin config
  {
    files,
    plugins: { n: nPlugin },
    rules: {
      ...nPlugin.configs['flat/recommended'].rules,
    },
  },

  // promise plugin config
  {
    files,
    plugins: { promise: promisePlugin },
    rules: {
      ...promisePlugin.configs['flat/recommended'].rules,
    },
  },

  // Overrides for typescript files
  {
    files: ['**/*.ts'],
    plugins: { '@typescript-eslint': tsPlugin },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      'no-undef': 'off',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@/func-call-spacing': ['error'],
      '@typescript-eslint/member-ordering': ['warn'],
      '@typescript-eslint/no-require-imports': ['error'],
    },
  },

  // Overrides for test files
  {
    files: ['**/*.test.js', '**/*.test.ts', '**/*.test.cjs', '**/*.test.mjs'],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      'no-undef': 'off',
    },
  },
];
