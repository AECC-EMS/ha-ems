# HA-EMS Integration for Home Assistant

[English](./README.md) | [简体中文](./README_zh.md)
# Integration Guide for HA-EMS Plugin with Home Assistant

This guide will help you integrate the `ha_ems_cloud` plugin into your Home Assistant instance and optionally set up a custom frontend panel.

## 📦 Download Installation Package

+ ✅ All-in-One ZIP Package:  
[Download Here](https://cdn.shuoxd.com/Aecc/HA/aecc-ha.zip )

## ⚙️ Install `ha_ems_cloud` (Cloud Plugin)

### Prerequisites

Before installing, ensure that your Home Assistant environment meets the following requirements:
+ Home Assistant Core ≥ 2025.2.1  
+ Operating System ≥ 13.0  

### Method 3: Manual Installation via [Samba](https://github.com/home-assistant/addons/tree/master/samba ) or [FTPS](https://github.com/hassio-addons/addon-ftp )

1. Extract the contents of `ha_ems_cloud.zip`.
2. Copy the extracted folder to the following directory in your Home Assistant configuration:


## 🔧 Configuration

### 🔐 Login

1. Go to **Settings > Devices & Services > Add Integration**  
   [Link to page](https://my.home-assistant.io/redirect/brand/?brand=xiaomi_home)
2. Search for `HA-EMS CLOUD`
3. Click Next
4. Click on the login link when prompted
5. Log in using your AECC APP account  
   *(If you don't have an AECC account, you can scan the QR code below to download the app and register an account and family)*

### ➕ Add Devices

After logging in successfully, a dialog box titled "Select Family" will appear. You can choose the family you want to add, and all devices within that family will be imported into Home Assistant.

## 🖥️ HA-EMS PANEL (Optional)

> If you do not wish to create a custom frontend page yourself, we provide a simple panel with basic data display and switch controls.

File structure:
```plain
{homeassistant_work_dir}/config
└── www/
    └── ha-ems-panel.mjs
```
### Installation Steps:
1. Copy the ha-ems-panel.mjs file from the downloaded package into your Home Assistant's config/www/ folder.
2. Edit your configuration.yaml file and add the following lines:
```
panel_custom:
  - name: ha-ems-panel
    sidebar_title: ems-panel # Customize this to your desired panel name
    sidebar_icon: mdi:chart-donut
    module_url: /local/ha-ems-panel.mjs
```
3. Save the file and restart Home Assistant.
4. Clear your browser cache and refresh the page to see the new panel.


