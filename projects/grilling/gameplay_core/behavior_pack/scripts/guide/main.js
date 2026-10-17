import { system } from '@minecraft/server';
import { installPublisher } from './publisher.js';
import { GUIDE_PAYLOAD } from './payload.js';
// Loaded once by Grilling scripts/main.js. The chapter UI belongs to Cookery.
try { installPublisher(system, GUIDE_PAYLOAD); }
catch (error) { console.warn(`[Grilling guide] Initialization failed: ${String(error)}`); }
