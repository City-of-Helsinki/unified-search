import type { Response } from 'express';

import packageJson from '../package.json' with { type: 'json' };

// Use this file's evaluation time as a fallback value for build time
const THIS_FILE_EVALUATION_TIME = new Date().toISOString();

export default function readiness(response: Response) {
  const release = process.env.APP_RELEASE ?? '';
  const packageVersion = packageJson.version;
  const commitHash = process.env.APP_COMMIT_HASH ?? '';
  const buildTime = process.env.APP_BUILD_TIME ?? THIS_FILE_EVALUATION_TIME;

  response.status(200).json({
    status: 'ok',
    release,
    packageVersion,
    commitHash,
    buildTime,
  });
}
