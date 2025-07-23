import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
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
