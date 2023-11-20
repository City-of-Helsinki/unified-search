module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
  },
  extends: ['standard-with-typescript', 'prettier'],
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 'latest',
    sourceType: 'module',
    tsconfigRootDir: __dirname,
    project: ['./tsconfig.json'],
  },
  rules: {
    '@typescript-eslint/indent': 'off',
    '@typescript-eslint/strict-boolean-expressions': 0,
    '@typescript-eslint/prefer-nullish-coalescing': 0,
    '@typescript-eslint/explicit-function-return-type': 0,
    '@typescript-eslint/naming-convention': 0,
    '@typescript-eslint/semi': 0,
    '@typescript-eslint/consistent-type-definitions': 0,
  },
  plugins: ['@typescript-eslint'],
};
