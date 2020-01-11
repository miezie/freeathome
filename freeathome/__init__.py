''' Main Home Assistant interface Free@Home '''
import logging
import voluptuous as vol
from homeassistant.helpers.discovery import load_platform
from homeassistant.core import CoreState, callback
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_PORT
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['slixmpp==1.4.2', 'libnacl==1.7.0']

DOMAIN = 'freeathome'

DATA_MFH = 'FAH'
CONF_USE_ROOM_NAMES = 'use_room_names'
DEFAULT_USE_ROOM_NAMES = False

# Validation of the user's configuration
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=5222): cv.port,
        vol.Optional(CONF_USERNAME, default='admin'): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_USE_ROOM_NAMES,
                     default=DEFAULT_USE_ROOM_NAMES): cv.boolean,
    })
}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    hass.async_create_task(
            hass.config_entries.flow.async_init(
                data={
                    "config": config.get(DOMAIN)
                },
            )
        )
    
    return True

async def async_setup_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    """ Setup of the Free@Home interface for Home Assistant ."""
    from . import pfreeathome

    config = entry.data["config"]

    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    sysap = pfreeathome.FreeAtHomeSysApp(host, port, username, password)
    sysap.use_room_names = config.get(CONF_USE_ROOM_NAMES)
    sysap.connect()

    hass.data[DATA_MFH] = sysap

    resp = await sysap.wait_for_connection()

    if resp:
        await sysap.find_devices()

        load_platform(hass, 'light', DOMAIN, {}, config)
        load_platform(hass, 'scene', DOMAIN, {}, config)
        load_platform(hass, 'cover', DOMAIN, {}, config)
        load_platform(hass, 'binary_sensor', DOMAIN, {}, config)
        load_platform(hass, 'climate', DOMAIN, {}, config)

        return True

    return False
