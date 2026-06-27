import { Router } from 'express';
import multer from 'multer';
import { createTicket } from '../controllers/ticketController';
import { ticketRateLimiter } from '../middleware/rateLimiter';
import { domainAuth } from '../middleware/domainAuth';
import { csrfProtection } from '../middleware/csrfProtection';
import { config } from '../config';

const storage = multer.memoryStorage();

const upload = multer({
  storage,
  limits: {
    fileSize: config.uploads.maxFileSizeMb * 1024 * 1024,
    files: config.uploads.maxFilesPerRequest,
  },
  fileFilter: (_req, file, cb) => {
    if (config.uploads.allowedMimeTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error(`Tipo de archivo no permitido: ${file.mimetype}`));
    }
  },
});

const router = Router();

router.post(
  '/',
  ticketRateLimiter,
  csrfProtection,
  upload.array('attachments', config.uploads.maxFilesPerRequest),
  domainAuth,
  createTicket
);

export default router;
