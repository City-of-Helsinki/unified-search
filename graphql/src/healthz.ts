import type { Response } from 'express';

export default function healthz(response: Response) {
  response.status(200).json({ status: 'ok' });
}
