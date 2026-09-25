import { system } from '@minecraft/server';
import { installPublisher } from './publisher.js';
import { GUIDE_PAYLOAD } from './payload.js';
// No direct access to host code, player language property, inventory, or world storage.
installPublisher(system, GUIDE_PAYLOAD);
