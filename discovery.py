# discovery.py
import logging
from zeroconf import ServiceStateChange
from zeroconf._services.info import AsyncServiceInfo

from .const import DOMAIN, BASE_URL, get_device_type_name  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)


def handle_zeroconf_callback(hass, entry, zeroconf, service_type, name, state_change):
    """同步包装器，用于调用异步函数"""
    hass.loop.call_soon_threadsafe(
        hass.async_create_task,
        async_handle_zeroconf_device(hass, entry, zeroconf, service_type, name, state_change)
    )


async def async_handle_zeroconf_device(hass, entry, zeroconf, service_type, name, state_change):
    """实际处理设备发现的异步逻辑"""
    info = AsyncServiceInfo(service_type, name)
    # 发起异步请求
    # _LOGGER.info(f"<MDNS 提取设备信息>: {info}")
    if state_change == ServiceStateChange.Added or state_change == ServiceStateChange.Updated:
        success = await info.async_request(zeroconf, timeout=3.0)
        if not success:
            return

        # 提取设备信息
        # device_sn = info.properties.get(b's_sn', b'').decode()
        properties = dict(info.properties)
        _LOGGER.info(f"<MDNS 提取设备信息>: {properties}")
        device_sn = properties.get(b's_sn', '').decode('utf-8')
        device_ip = properties.get(b's_ip', '').decode('utf-8')
        device_type = int(properties.get(b's_type', '0').decode('utf-8'))
        device_port = int(properties.get(b's_port', 0).decode('utf-8'))

        _LOGGER.info(f"<设备数据s>: {hass.data[DOMAIN]['device_manager'].devices}")
        # 匹配云端设备并更新配置条目
        # device_registry = dr.async_get(hass)
        # device = device_registry.async_get_device(identifiers={(DOMAIN, device_sn)})
        for device in hass.data[DOMAIN]['device_manager'].devices:
            _LOGGER.info(f"<设备数据>: {device.device_sn},{device_sn}")
            if device and device.device_sn and device.device_sn == device_sn:
                # config_entry = hass.config_entries.async_get_entry()
                # if config_entry:
                _LOGGER.info(f"<设备数据>: {device.device_sn},{device_sn}")
                device.local_ip = device_ip
                device.local_port = device_port
                device.local_type = get_device_type_name(device_type)
                device.is_local=True
                # hass.config_entries.async_update_entry(config_entry, data=new_data)
                _LOGGER.info(f"设备 {device_sn} 的本地信息已更新: {device_ip}:{device_port}-{get_device_type_name(device_type)}")
        for device in hass.data[DOMAIN]['device_manager'].devices:
            _LOGGER.info(f"<设备数据后>: {device.device_sn},{device.is_local}")
    if state_change == ServiceStateChange.Removed:
        success = await info.async_request(zeroconf, timeout=3.0)
        if not success:
            return

        # 提取设备信息
        # device_sn = info.properties.get(b's_sn', b'').decode()
        properties = dict(info.properties)
        device_sn = properties.get(b's_sn', '').decode('utf-8')
        device_ip = properties.get(b's_ip', '').decode('utf-8')
        device_type = int(properties.get(b's_type', '0').decode('utf-8'))
        device_port = int(properties.get(b's_port', 0).decode('utf-8'))
        _LOGGER.info(f"<MDNS 提取设备信息>: {info.properties}")

        # 匹配云端设备并更新配置条目
        # device_registry = dr.async_get(hass)
        # device = device_registry.async_get_device(identifiers={(DOMAIN, device_sn)})

        for device in hass.data[DOMAIN]['device_manager'].devices:
            if device and device.device_sn and device.device_sn == device_sn:
                # config_entry = hass.config_entries.async_get_entry()
                # if config_entry:
                device.is_local=False
                # hass.config_entries.async_update_entry(config_entry, data=new_data)
                _LOGGER.info(f"设备 {device_sn} 的本地信息已更新: {device_ip}:{device_port}-device_type")