from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

# 定义哪些字段作为 switch 暴露出去
SWITCH_MAP = {
    "PlugInfoList": {
        "status": ("PlugStatus", "Switch"),
    },
    "ChargerInfoList": {
        "status": ("ChargerStatus", "Switch"),
    },
    "HotInfoList": {
        "status": ("HotStatus", "Switch"),
    }
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """从配置项中初始化设备，并添加 switch 实体"""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    device_sn = config_entry.data["device_sn"]

    switches = []

    # 处理 Switch
    for data_type, field_map in SWITCH_MAP.items():
        raw_data = coordinator.data.get(data_type)
        if not raw_data:
            continue

        if isinstance(raw_data, list):
            for item in raw_data:
                sn = item.get("PlugSN") or item.get("ChargerSN") or item.get("HotSN")
                if not sn:
                    continue

                for key, (path, name) in field_map.items():
                    value = item.get(path)
                    if value is None:
                        continue
                    attr = {
                        "dev_addr": item.get("DevAddr"),
                        "is_third_party": item.get("lsThirdParty"),
                        "fans_dev_type": item.get("FansDevType"),
                        "is_interconnect": item.get("IsInterconnect"),
                    }
                    switches.append(
                        AECCSwitch(coordinator, device_sn, item, data_type, key, path, name, attr)
                    )

    async_add_entities(switches)


class AECCSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, device_sn, item, data_type, key, path, name, attr):
        super().__init__(coordinator)
        self._item = item
        self._data_type = data_type
        self._device_sn = device_sn
        self._key = key
        self._path = path
        self._name = name
        self._unique_id = self._generate_unique_id(device_sn, item)
        self._attr = attr
        _LOGGER.info(f"self._state: {self._item.get(self._path)}")
        self._state= self._item.get(self._path)

    def _generate_unique_id(self, device_sn, item):
        sn = item.get("PlugSN") or item.get("ChargerSN") or item.get("HotSN")
        if sn:
            return f"aecc_{device_sn}_{self._data_type.lower()}_{sn}_{self._key}"
        else:
            return f"aecc_{device_sn}_{self._data_type.lower()}_{self._key}"
    @property
    def name(self):
        sn = self._item.get("PlugSN") or self._item.get("ChargerSN") or self._item.get("HotSN")
        if sn:
            return f"{sn} {self._key.replace('_', ' ').title()}"
        else:
            return f"{self._key.replace('_', ' ').title()}"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def is_on(self):
          return  True if self._state==1 else False

    async def async_turn_on(self, **kwargs):
        """发送打开命令"""
        sn = self._item.get("PlugSN") or self._item.get("ChargerSN") or self._item.get("HotSN")
        if sn:
            _LOGGER.info(f"Turning on switch: {sn}")
            # 假设 client 提供了 turn_on_plug 方法
            await self.coordinator.client.turn_on_switch(self._attr)
            self._state = 1

            await self.coordinator.async_request_refresh()
    async def async_turn_off(self, **kwargs):
        """发送关闭命令"""
        sn = self._item.get("PlugSN") or self._item.get("ChargerSN") or self._item.get("HotSN")
        if sn:
            _LOGGER.info(f"Turning off switch: {sn}")
            await self.coordinator.client.turn_off_switch(self._attr)
            self._state = 0
            await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_sn)},
            "name": self._device_sn,
        }
    @property
    def extra_state_attributes(self) :
        return self._attr