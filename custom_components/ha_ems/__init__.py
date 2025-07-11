"""The Detailed Hello World Push integration."""
from datetime import timedelta

import logging
from functools import partial

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.const import Platform

from .hub import MyIntegrationHub
from .const import DOMAIN, BASE_URL  # pylint:disable=unused-import

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]  # 添加 Platform.SWITCH
SCAN_INTERVAL = timedelta(seconds=10)
_LOGGER = logging.getLogger(__name__)

# __init__.py
# __init__.py
from .discovery import handle_zeroconf_callback



from zeroconf import ServiceStateChange, ServiceBrowser
from .const import DOMAIN


async def async_setup_entry(hass, entry):
        """Set up the sensor platform from a config entry."""
        # Initialize your integration here (e.g., fetch data)
        hass.data.setdefault(DOMAIN, {})

        # _LOGGER.info(f"plant:{entry.data['devices']}")
        hub = MyIntegrationHub(
            hass,
            entry.data["username"],
            entry.data["password"],
            entry.data["selected_device_id"],
        )
        hass.data[DOMAIN]['hub'] = hub
        hass.data[DOMAIN]['cur_plant_name']= entry.data["selected_device_name"]

        # 创建设备实体管理器
        from .device_entity_manager import DeviceEntityManager
        device_manager = DeviceEntityManager(hass, hub)
        hass.data[DOMAIN]['device_manager'] = device_manager




        # local
        # _LOGGER.info(f"Setting up AECC device entry {entry.data}")

        # 获取配置信息
        # host = entry.data["device_ip"]
        # port = entry.data["device_port"]



        # 获取设备数据并创建实体
        await hub.login()
        await hub.getPlantVos()
        await hub.get_home_control_devices()
        device_data = await hub.getHomeCountData()
        if device_data:
            _LOGGER.info(f"设备数据: {device_data}")
            entities = await device_manager.create_entities_from_data(device_data)
            _LOGGER.info(f"创建的实体: {entities}")
            _LOGGER.info(f"创建的设备: {device_manager.devices}")

            if entities:
                # for platform in PLATFORMS:
              await  hass.async_create_task(
                    hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
              )
        await hub.start_polling()
        await hub.start_schedule_login()



        # 获取 Zeroconf 实例
        zeroconf_instance = await zeroconf.async_get_async_instance(hass)

        ServiceBrowser(
            zeroconf_instance.zeroconf,
            "_http._tcp.local.",
            handlers=[partial(handle_zeroconf_callback, hass, entry)]
        )

        _LOGGER.info(f"Zeroconf 实例:{zeroconf_instance}")




        """注册服务   先这么写，后期再优化"""
        #电站切换api
        async def async_switch_plant_service(call):
            """服务处理函数：调用服务"""
            plant_id =call.data['plant_id']
            device_sn = call.data['device_sn']
            # _LOGGER.info(f"plant_id: {plant_id}")
            hub = hass.data[DOMAIN]['hub']
            hub.senceId=str(plant_id)
            if device_sn is not None and device_sn != '':
                hub.cur_ctl_devices=device_sn
            hass.data[DOMAIN]['cur_plant_name']=str(plant_id)
            await hub.async_update_data()
        # 注册电站服务
        hass.services.async_register(
            DOMAIN,
            "service_switch_plant",
            async_switch_plant_service,
        )

        # 注册获取电站每日统计数据
        async def async_get_energy_data_day(call):
            await hub.get_energy_data_day(hub.senceId)

        hass.services.async_register(
            DOMAIN,
            "service_get_energy_data_day",
            async_get_energy_data_day,
        )

        # 注册获取电站每日统计数据
        async def async_get_energy_data_month(call):
            await hub.get_energy_data_month(hub.senceId)

        hass.services.async_register(
            DOMAIN,
            "service_get_energy_data_month",
            async_get_energy_data_month,
        )

        # 注册获取电站每日统计数据
        async def async_get_energy_data_year(call):
             await hub.get_energy_data_year(hub.senceId)

        hass.services.async_register(
            DOMAIN,
            "service_get_energy_data_year",
            async_get_energy_data_year,
        )

        # 注册获取电站每日统计数据
        async def async_get_energy_data_total(call):
             await hub.get_energy_data_total(hub.senceId)

        hass.services.async_register(
            DOMAIN,
            "service_get_energy_data_total",
            async_get_energy_data_total,
        )

        # 立即刷新主页数据
        async def refresh_data(call):
            await hub.async_update_data()

        hass.services.async_register(
            DOMAIN,
            "service_refresh_data",
            refresh_data,
        )

        # 注册卸载回调
        entry.async_on_unload(entry.add_update_listener(async_update_listener))

        return True



async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
        entry.async_on_unload(hass.data[DOMAIN]['hub'].stop_polling)

        # 可选：断开 TCP 连接
        client = hass.data[DOMAIN][entry.entry_id].get("client")
        if client and hasattr(client, "disconnect"):
            await client.disconnect()
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id)
        return unload_ok

async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """处理配置条目更新。"""
    await hass.config_entries.async_reload(entry.entry_id)
