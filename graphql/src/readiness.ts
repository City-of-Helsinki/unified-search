import { statSync } from 'fs';
import { fileURLToPath } from 'url';

import type { Response } from 'express';

import packageJson from '../package.json' with { type: 'json' };

// Use this file's modification time as a workaround for app build time
const THIS_FILE_MODIFICATION_TIME = new Date(
  statSync(fileURLToPath(import.meta.url)).mtime
).toISOString();

export function makeReadinessResultObject() {
  const release = process.env.APP_RELEASE ?? '';
  const packageVersion = packageJson.version;
  const commitHash = process.env.APP_COMMIT_HASH ?? '';
  const buildTime = process.env.APP_BUILD_TIME ?? THIS_FILE_MODIFICATION_TIME;

  return {
    status: 'ok',
    release,
    packageVersion,
    commitHash,
    buildTime,
  };
}

export default function readiness(response: Response) {
  response.status(200).json(makeReadinessResultObject());
}
