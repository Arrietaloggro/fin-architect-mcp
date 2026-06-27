import { Router } from 'express';
import { getPublicConfig } from '../controllers/configController';
import { csrfTokenHandler } from '../middleware/csrfProtection';
import { configRateLimiter } from '../middleware/rateLimiter';

const router = Router();

router.get('/', configRateLimiter, getPublicConfig);
router.get('/csrf-token', configRateLimiter, csrfTokenHandler);

export default router;
