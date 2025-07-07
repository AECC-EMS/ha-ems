# local_scanner.py - 后台自动扫描任务
from zeroconf import ServiceBrowser, ServiceStateChange
import logging

from homeassistant.components import zeroconf
from .const import DOMAIN, LOGGER_NAME
_LOGGER = logging.getLogger(LOGGER_NAME)

class LocalScanner:
    def __init__(self, hass, config_entry):
        self.hass = hass
        self.config_entry = config_entry
        self.zeroconf = None
        self.browser = None
        self.is_running = False

    async def start_scanning(self):
        self.is_running = True
        self.zeroconf = await zeroconf.get_async_zeroconf_instance()

        self.browser = ServiceBrowser(
            self.zeroconf,
            "_http._tcp.local.",
            handlers=[self.on_service_state_change]
        )

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            # 解析设备信息
            ip, port = self.resolve_service(name)
            local_device = self.get_device_details(ip, port)
            # 匹配云端设备并更新优先级
            cloud_device = self.device_manager.match_local_to_cloud(local_device)
            if cloud_device:
                self.device_manager.update_device_priority(
                    cloud_device.id, "local", ip
                )