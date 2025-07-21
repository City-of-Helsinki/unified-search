import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
    coverage: {
      reporter: ['text', 'lcov'],
    },
    include: ['src/**/*.test.{js,ts,jsx,tsx}'],
  },
});

