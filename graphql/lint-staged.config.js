/**
 * @type {import('lint-staged').Configuration}
 */
export default {
  'src/**/*.{js,jsx,ts,tsx,cjs,mjs}': [
    'eslint --fix',
    'prettier --write',
    // https://vitest.dev/guide/cli.html#vitest-related
    'vitest related --run',
  ],
};
