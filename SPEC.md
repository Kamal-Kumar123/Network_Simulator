# ITL351 — Network Protocol Simulator — Specification

**Course:** ITL351 Computer Networks Lab  
**Submission 1 (deadline 25 March 2026)**  
**Implementation:** Python 3.10+, PyQt5 GUI, stdlib + PyQt5 only.

## 1. Purpose

Desktop simulator for teaching physical and data-link behaviour: hubs, switches, bridges, CRC, CSMA/CD, Go-Back-N, Selective Repeat, with a graphical topology canvas and event log.

## 2. How to run

- **GUI:** `python main.py`
- **Headless tests / demos:** `python main.py --headless`

## 3. Mapping to assignment (Submission 1)

### Physical layer (minimum)

| Requirement | Implementation |
|-------------|----------------|
| End devices | `physical/end_device.py` — `EndDevice` |
| Hubs | `physical/hub.py` — `Hub` (repeat to all ports except ingress) |
| Connections | `NetworkState.connections` + optional `physical/connection.py` model |
| Send/receive | `Simulator.send_frame` → `_deliver` → hubs/switches/hosts |

**Test cases**

- Two PCs, dedicated link: Scenario **1a** (toolbar / headless).
- Star, 5 PCs + hub: Scenario **1b**; broadcast uses receiver **`(Broadcast)`** in GUI.

### Data link layer (minimum)

| Requirement | Implementation |
|-------------|----------------|
| Switch, bridge | `datalink/switch.py`, `datalink/bridge.py` |
| Switch learning | MAC table on unknown dest → flood; known → unicast |
| Error control | `datalink/error_control.py` — CRC polynomial `1101` |
| Access control | `datalink/access_control.py` — CSMA/CD (optional on send) |
| Sliding window | `datalink/flow_control.py` — Go-Back-N, Selective Repeat |

**Test cases**

- Switch + 5 PCs + domains + flow/access: Scenario **2a** + Control panel (CSMA) + Flow panel (GBN/SR).
- Two hubs + switch + 10 PCs: Scenario **2b**; hub–switch paths use `core/dispatch.relay_frame`.

### Add-ons (partial)

- Bits / NRZ-style groups: `Frame.to_bits()` in send logs.
- Topology: `gui/canvas.py`.
- Noise: `CRC.introduce_error` + “Inject bit error” on send when CRC enabled.
- CRC demo panel: `CRCDemoPanel` + `Simulator.crc_demo_report`.

## 4. Architecture rules

- `gui/` imports **`simulator/`** only (not `physical/` / `datalink/` directly in widgets; logic goes through `Simulator`).
- Protocol logic stays out of GUI handlers where possible.
- `NetworkState` is a singleton (`get_instance()`).

## 5. Domain counts

- Per-device lines list each device’s `get_collision_domains()` / `get_broadcast_domains()`.
- **Total** line for the “two hubs + one switch (uplinks only)” topology uses **3 collision domains** and **1 broadcast domain** (assignment-style interpretation for Scenario 2b).

## 6. Revision history

| Date | Notes |
|------|--------|
| 2026-03-15 | Initial SPEC; hub↔switch relay, CRC on send, broadcast receiver, CRC demo panel, SPEC.md |
