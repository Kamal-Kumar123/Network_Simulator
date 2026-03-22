from __future__ import annotations

import sys

from core.network_state import NetworkState
from datalink.error_control import CRC
from simulator.engine import BROADCAST_RECEIVER, Simulator
from gui.app import launch_gui


def run_all_tests() -> None:
    """Run all required headless scenarios and demos."""
    sim = Simulator()
    state = sim.state

    def print_events(title: str) -> None:
        print("=" * 40)
        print(title)
        print("=" * 40)
        for e in state.events:
            print(f"[{e.level}] {e.message}")
        print()
        state.events.clear()

    # Scenario 1a
    sim.reset()
    pc1 = sim.add_device("PC1", "AA:BB:CC:00:00:01")
    pc2 = sim.add_device("PC2", "AA:BB:CC:00:00:02")
    sim.connect("PC1", "PC2")
    sim.send_frame("PC1", "PC2", "Hello PC2!", True, False, False)
    print_events("Scenario 1a - Two PCs, direct link")
    print(sim.get_domain_report())
    print("\n")

    # Scenario 1b
    sim.reset()
    hub = sim.add_hub("Hub1")
    for i in range(1, 6):
        name = f"PC{i}"
        mac = f"AA:BB:CC:00:01:0{i}"
        sim.add_device(name, mac)
        sim.connect(name, "Hub1")
    sim.send_frame("PC1", BROADCAST_RECEIVER, "Hello everyone!", True, False, False)
    print_events("Scenario 1b - Star topology: Hub + 5 PCs")
    print(sim.get_domain_report())
    print("\n")

    # Scenario 2a
    sim.reset()
    sim.add_switch("SW1")
    for i in range(1, 6):
        name = f"PC{i}"
        mac = f"AA:BB:CC:00:02:0{i}"
        sim.add_device(name, mac)
        sim.connect(name, "SW1")
    sim.send_frame("PC1", "PC3", "Hello PC3", True, False, False)
    sim.send_frame("PC2", "PC4", "Hello PC4", True, False, False)
    print_events("Scenario 2a - Switch + 5 PCs")
    print(sim.get_domain_report())
    print("\n")

    # Scenario 2b
    sim.reset()
    sim.add_switch("SW1")
    sim.add_hub("Hub1")
    sim.add_hub("Hub2")
    sim.connect("Hub1", "SW1")
    sim.connect("Hub2", "SW1")
    for i in range(1, 6):
        name = f"PC{i}"
        mac = f"AA:BB:CC:00:03:0{i}"
        sim.add_device(name, mac)
        sim.connect(name, "Hub1")
    for i in range(6, 11):
        name = f"PC{i}"
        mac = f"AA:BB:CC:00:03:{i:02d}"
        sim.add_device(name, mac)
        sim.connect(name, "Hub2")
    sim.send_frame("PC1", "PC8", "Hello PC8", True, False, False)
    sim.send_frame("PC10", "PC3", "Hello PC3", True, False, False)
    print_events("Scenario 2b - Two hub-groups via switch (10 PCs)")
    print(sim.get_domain_report())
    print("\n")

    # CRC demo
    raw = "11010011101100"
    with_crc = CRC.attach(raw)
    print("=" * 40)
    print("CRC demo")
    print("=" * 40)
    print(f"Original:     {raw}")
    print(f"With CRC:     {with_crc}")
    print(f"Verify OK:    {CRC.verify(with_crc)}")
    corrupted = CRC.introduce_error(with_crc)
    print(f"Corrupted:    {corrupted}")
    print(f"Verify after: {CRC.verify(corrupted)}")
    print()

    # Go-Back-N demo
    frames = ["F0", "F1", "F2", "F3", "F4"]
    sim.reset()
    print("=" * 40)
    print("Go-Back-N demo")
    print("=" * 40)
    sim.run_go_back_n(frames, window=4, error_at=2)
    for e in state.events:
        print(f"[{e.level}] {e.message}")
    state.events.clear()
    print()

    # Selective Repeat demo
    print("=" * 40)
    print("Selective Repeat demo")
    print("=" * 40)
    sim.run_selective_repeat(frames, window=4, error_at=3)
    for e in state.events:
        print(f"[{e.level}] {e.message}")
    state.events.clear()


if __name__ == "__main__":
    if "--headless" in sys.argv:
        run_all_tests()
    else:
        launch_gui()

