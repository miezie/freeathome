""" Support for Free@Home Lock through 7 inch panel """
import logging
from homeassistant.components.lock import (LockEntity)
import custom_components.freeathome as freeathome

REQUIREMENTS = ['slixmpp==1.5.1']

DEPENDENCIES = ['freeathome']

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """ setup """

    _LOGGER.info('FreeAtHome setup lock controll')

    fah = hass.data[freeathome.DATA_MFH]

    devices = fah.get_devices('lock')

    for device, device_object in devices.items():
        async_add_devices([FreeAtHomeLock(device_object)])

class FreeAtHomeLock(LockEntity):
    ''' Interface to the lock entities of Free@Home '''
    _name = ''
    lock_device = None
    _state = None

    def __init__(self, device):
        self.lock_device = device
        self._name = self.lock_device.name
        self._is_locked = (self.lock_device.state == '0')

    @property
    def name(self):
        """Return the display name of the lock."""
        return self._name

    @property
    def unique_id(self):
        """Return the ID """
        return self.lock_device.device_id

    @property
    def should_poll(self):
        """Return that polling is not necessary."""
        return False

    @property 
    def is_locked(self):
        """Return true if device is on."""
        return self._is_locked
    
    async def async_added_to_hass(self):
        """Register callback to update hass after device was changed."""
        async def after_update_callback(device):
            """Call after device was updated."""
            await self.async_update_ha_state(True)
        self.lock_device.register_device_updated_cb(after_update_callback)

    async def async_update(self):
        """Retrieve latest state."""
        self._is_locked = (self.lock_device.state == '0')

    async def async_lock(self, **kwargs):
        """Lock the device."""
        await self.lock_device.lock()

    async def async_unlock(self, **kwargs):
        """Unlock the device."""
        await self.lock_device.unlock()    
