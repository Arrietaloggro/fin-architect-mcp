import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import { config } from './config';
import { requestLogger } from './middleware/requestLogger';
import ticketRoutes from './routes/tickets';
import configRoutes from './routes/config';
import adminRoutes from './routes/admin';

const app = express();

// Security headers
app.use(helmet({
  contentSecurityPolicy: config.isProduction ? undefined : false,
}));

// CORS
app.use(cors({
  origin: config.cors.origin,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-CSRF-Token'],
  credentials: true,
}));

// Compression & parsing
app.use(compression());
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// Trust proxy for real IPs behind load balancers
app.set('trust proxy', 1);

// Request logging
app.use(requestLogger);

// Health check
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString(), env: config.env });
});

// API routes
app.use('/api/config', configRoutes);
app.use('/api/tickets', ticketRoutes);
app.use('/api/admin', adminRoutes);

// 404 handler
app.use((_req, res) => {
  res.status(404).json({ error: 'Endpoint no encontrado.' });
});

// Global error handler
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  if (err.message.includes('Tipo de archivo no permitido')) {
    res.status(400).json({ error: err.message });
    return;
  }
  if (err.message.includes('File too large')) {
    res.status(400).json({ error: `El archivo supera el límite de ${config.uploads.maxFileSizeMb}MB.` });
    return;
  }
  res.status(500).json({ error: 'Error interno del servidor.' });
});

export default app;
