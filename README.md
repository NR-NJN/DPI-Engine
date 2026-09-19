# DPI-Engine

> A lightweight, low-latency Deep Packet Inspection and routing engine optimized for the STM32 microcontroller ecosystem. 

## 🚀 Overview

**DPI-Engine** brings Deep Packet Inspection and advanced routing capabilities to edge devices. Designed specifically for embedded environments, this engine parses network traffic directly on device, 
extracting packet metadata and applying rule based filtering with a strictly constrained memory footprint. It couples packet inspection with Equal Cost Multi Path routing concepts to efficiently load balance 
and direct network traffic at the edge.

## ✨ Key Features

- **Embedded DPI Pipeline:** Memory-efficient parsing of L3 (IPv4) and L4 (TCP/UDP) headers, tailored for the resource constraints of an ARM Cortex-M microcontroller.
- **Equal-Cost Multi-Path Routing:** Integrates ECMP logic to distribute network traffic efficiently across multiple available paths based on extracted packet flows.
- **SPI Communication Interface:** Leverages the SPI bus for high speed data extraction and peripheral communication, minimizing CPU polling overhead.
- **Zero-Copy Processing:** Processes packet buffers directly in memory to maintain low latency and avoid costly memory duplication on the MCU.
- **Rule-Based Filtering:** Configurable ruleset to drop or forward incoming traffic based on IP, ports, or protocol signatures.

## 🧰 Hardware Requirements

This project is configured and tested for the **STM32 B-L475E-IOT01A** Discovery kit, but the core engine logic is portable across the broader STM32 family.

- **Microcontroller:** STM32 B-L475E-IOT01A i.e ARM Cortex-M4
- **Debugger/Programmer:** On-board ST-LINK/V2-1
- **Network Interface:** On-board Wi-Fi module 

## 🏗️ System Architecture

```text
+------------------------+
| Network Interface (RX) |
+-----------+------------+
            | (SPI / Interrupts)
            v
+------------------------+
|  Packet Buffer Memory  |
+-----------+------------+
            |
            v
+------------------------+      +------------------+
|    DPI Parse Engine    | ---> | Rule Match Logic |
|  (L3/L4 Extraction)    | <--- | (Drop / Forward) |
+-----------+------------+      +------------------+
            |
            v
+------------------------+
|  ECMP Routing Engine   | <-- Determines optimal output path
+-----------+------------+
            |
            v
+------------------------+
| Network Interface (TX) |
+------------------------+
```
## Run
Open in VSCode/CodeOSS:

    Launch STM32CubeIDE.

    Navigate to File -> Open Projects from File System...

    Select the cloned DPI-Engine directory.

Build the Project:

    Click the Build icon or press Ctrl+B to compile the firmware.

Flash to the MCU:

    Connect your STM32 B-L475E-IOT01A board via USB.

    Click the Run or Debug icon to flash the compiled binary to the microcontroller via the integrated ST-LINK.
Run the python shell script to send packets and/or mimic an attack
