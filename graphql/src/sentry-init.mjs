// @sentry/node initialization needs to be in its own file, see "instrument.js" in
// https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.SENTRY_ENVIRONMENT,
});
