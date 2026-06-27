import { Router } from 'express';
import { adminAuth } from '../middleware/adminAuth';
import { adminRateLimiter } from '../middleware/rateLimiter';
import {
  getConfig,
  updateConfig,
  patchSection,
  getHistory,
  getHistoryById,
  getStats,
  getIntercomSyncStatus,
  getIntercomSyncHistory,
  triggerIntercomSync,
} from '../controllers/adminController';

const router = Router();

router.use(adminRateLimiter, adminAuth);

router.get('/config', getConfig);
router.put('/config', updateConfig);
router.patch('/config/products', patchSection('products'));
router.patch('/config/request-types', patchSection('requestTypes'));
router.patch('/config/priorities', patchSection('priorities'));
router.patch('/config/teams', patchSection('teams'));

router.get('/history', getHistory);
router.get('/history/:id', getHistoryById);
router.get('/stats', getStats);

router.get('/intercom/status', getIntercomSyncStatus);
router.get('/intercom/sync-history', getIntercomSyncHistory);
router.post('/intercom/sync', triggerIntercomSync);

export default router;
