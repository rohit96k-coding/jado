
import asyncio
from kasa import Discover, SmartPlug, SmartBulb

class KasaAgent:
    def __init__(self):
        self.devices = {}

    async def discover_devices(self):
        """Scans network for TP-Link Kasa devices."""
        self.devices = await Discover.discover()
        return list(self.devices.keys())

    async def turn_on(self, alias):
        dev = self._find_by_alias(alias)
        if dev:
            await dev.update()
            await dev.turn_on()
            return f"Turned on {alias}."
        return f"Device {alias} not found."

    async def turn_off(self, alias):
        dev = self._find_by_alias(alias)
        if dev:
            await dev.update()
            await dev.turn_off()
            return f"Turned off {alias}."
        return f"Device {alias} not found."

    def _find_by_alias(self, alias):
        for ip, dev in self.devices.items():
            if dev.alias.lower() == alias.lower():
                return dev
        return None

    # Sync Wrappers for Main Thread
    def execute(self, action, device_name):
        try:
            if action == "discover":
                return asyncio.run(self.discover_devices())
            elif action == "on":
                return asyncio.run(self.turn_on(device_name))
            elif action == "off":
                return asyncio.run(self.turn_off(device_name))
        except Exception as e:
            return f"Smart Home Error: {e}"
