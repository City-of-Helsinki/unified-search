import { describe, it, vi, expect, afterEach } from 'vitest';

import packageJson from '../../package.json' with { type: 'json' };
import {
  makeReadinessResultObject,
  default as readiness,
} from '../readiness.js';

const ORIGINAL_PROCESS_ENV = { ...process.env };

const restoreProcessEnv = () => {
  process.env = { ...ORIGINAL_PROCESS_ENV };
};

describe('makeReadinessResultObject', () => {
  afterEach(restoreProcessEnv);

  it('returns ok status with values from package.json and environment variables', () => {
    process.env.APP_RELEASE = 'test-release-v1.2.3';
    process.env.APP_COMMIT_HASH = 'abc123';
    process.env.APP_BUILD_TIME = '2025-12-30T12:34:45.000Z';

    const result = makeReadinessResultObject();
    expect(result).toStrictEqual({
      status: 'ok',
      release: 'test-release-v1.2.3',
      packageVersion: packageJson.version,
      commitHash: 'abc123',
      buildTime: '2025-12-30T12:34:45.000Z',
    });
  });
});

describe('readiness', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('calls response.status(200) and response.json(makeReadinessResultObject())', () => {
    const statusMock = vi.fn().mockReturnThis();
    const jsonMock = vi.fn();
    const response = { status: statusMock, json: jsonMock };

    // @ts-expect-error Mocking doesn't satisfy the Response type, but that's ok for testing
    readiness(response);

    expect(statusMock).toHaveBeenCalledWith(200);
    expect(jsonMock).toHaveBeenCalledWith(makeReadinessResultObject());
  });
});
