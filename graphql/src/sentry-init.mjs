// @sentry/node initialization needs to be in its own file, and this file must
// be imported before any other module in this application. See "instrument.js"
// and "Require instrument.js before any other module in your application" in
// https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.SENTRY_ENVIRONMENT,
});
