// Extend Express Request to carry per-request context
declare global {
  namespace Express {
    interface Request {
      requestId?: string;
    }
  }
}

export {};
