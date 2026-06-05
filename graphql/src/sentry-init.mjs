// @sentry/node initialization needs to be in its own file, and this file must
// be imported before any other module in this application. See "instrument.js"
// and "Require instrument.js before any other module in your application" in
// https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/
import * as Sentry from '@sentry/node';
import { nodeProfilingIntegration } from '@sentry/profiling-node';

const ignoredTracePaths = (
  process.env.SENTRY_TRACES_IGNORE_PATHS || '/healthz,/readiness'
)
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

/**
 * Parse a string value to a floating point number.
 * If the value is not a valid number, returns the fallback value.
 */
const parseSampleRate = (value, fallback) => {
  if (value === undefined || value === null || value === '') {
    return fallback;
  }
  const parsed = Number(value);
  return Number.isNaN(parsed) ? fallback : parsed;
};

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.SENTRY_ENVIRONMENT,
  release: process.env.SENTRY_RELEASE,
  integrations: [nodeProfilingIntegration()],
  tracesSampler: (samplingContext) => {
    const { attributes } = samplingContext;
    const requestPath = attributes?.['http.target'];

    if (
      requestPath &&
      ignoredTracePaths.some((path) => requestPath.startsWith(path))
    ) {
      return 0;
    }

    return parseSampleRate(process.env.SENTRY_TRACES_SAMPLE_RATE, 0);
  },
  profileSessionSampleRate: parseSampleRate(
    process.env.SENTRY_PROFILE_SESSION_SAMPLE_RATE,
    0
  ),
  profileLifecycle: 'trace',
});
