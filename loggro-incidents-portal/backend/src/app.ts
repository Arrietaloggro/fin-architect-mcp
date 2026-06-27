import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import path from 'path';
import fs from 'fs';
import { config } from './config';
import { requestLogger } from './middleware/requestLogger';
import { logger } from './utils/logger';
import ticketRoutes from './routes/tickets';
import configRoutes from './routes/config';
import adminRoutes from './routes/admin';

const app = express();

// Security headers — full CSP in all environments
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],   // needed for Vite dev
      styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
      fontSrc: ["'self'", 'https://fonts.gstatic.com'],
      imgSrc: ["'self'", 'data:'],
      connectSrc: ["'self'"],
    },
  },
  crossOriginEmbedderPolicy: false,
}));

// CORS — strict: only configured origins
const allowedOrigins = config.cors.origin.split(',').map((o) => o.trim());
app.use(cors({
  origin: (origin, cb) => {
    // Allow requests with no origin (e.g. curl, same-origin in prod)
    if (!origin || allowedOrigins.includes(origin)) return cb(null, true);
    logger.warn('CORS blocked request', { origin });
    cb(new Error('Not allowed by CORS'));
  },
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-CSRF-Token'],
  credentials: true,
}));

// Compression & parsing
app.use(compression());
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// Trust proxy for real IPs behind load balancers / Railway / Vercel
app.set('trust proxy', 1);

// Request logging
app.use(requestLogger);

// Health check (no auth, no rate limit — needed by Railway/Render)
app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    env: config.env,
    version: process.env.npm_package_version ?? '1.0.0',
  });
});

// API routes
app.use('/api/config', configRoutes);
app.use('/api/tickets', ticketRoutes);
app.use('/api/admin', adminRoutes);

// Serve compiled frontend in production
const frontendDist = path.resolve(__dirname, '../../frontend/dist');
if (config.isProduction && fs.existsSync(frontendDist)) {
  app.use(express.static(frontendDist));
  app.get('*', (_req, res) => {
    res.sendFile(path.join(frontendDist, 'index.html'));
  });
}

// 404 handler (API only in dev, all routes in prod if no frontend)
app.use((_req, res) => {
  res.status(404).json({ error: 'Endpoint no encontrado.' });
});

// Global error handler — typed correctly for Express 4
// eslint-disable-next-line @typescript-eslint/no-unused-vars
app.use((err: Error & { status?: number; code?: string }, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  if (err.message === 'Not allowed by CORS') {
    res.status(403).json({ error: 'Origen no permitido.' });
    return;
  }
  if (err.message?.includes('Tipo de archivo no permitido')) {
    res.status(400).json({ error: err.message });
    return;
  }
  if (err.message?.includes('File too large') || err.code === 'LIMIT_FILE_SIZE') {
    res.status(400).json({ error: `El archivo supera el límite de ${config.uploads.maxFileSizeMb}MB.` });
    return;
  }
  if (err.code === 'LIMIT_FILE_COUNT') {
    res.status(400).json({ error: `Máximo ${config.uploads.maxFilesPerRequest} archivos por solicitud.` });
    return;
  }
  // Log unexpected errors only
  logger.error('Unhandled server error', { error: err.message, stack: err.stack });
  res.status(err.status || 500).json({ error: 'Error interno del servidor. Por favor intenta nuevamente.' });
});

export default app;
