import { loadEnv } from 'vite';
import { defineConfig } from 'vitest/config';

import { findClosestEnvFile } from './src/utils.js';

const ENV_FILE_PATH = findClosestEnvFile();

export default defineConfig({
  test: {
    ...(ENV_FILE_PATH
      ? {
          env:
            // Loads all env vars from the following env files:
            // .env
            // .env.local
            // .env.[mode] i.e. .env.test
            // .env.[mode].local i.e. .env.test.local
            //
            // NOTE: If mode is set to '', the files '.env.' and '.env..local'
            //       would be loaded, which is unwanted, so chose mode 'test'.
            loadEnv('test', ENV_FILE_PATH, ''),
        }
      : {}),
    environment: 'node',
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['lcov', 'html'],
      exclude: ['**/__snapshots__/**', '**/__tests__/**', '**/node_modules/**'],
    },
    include: ['src/**/*.test.{js,ts,cjs,mjs}'],
  },
});
