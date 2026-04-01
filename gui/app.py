from __future__ import annotations

from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QToolBar,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)

from core.network_state import EventLog, NetworkState
from gui.canvas import TopologyCanvas
from gui.dialogs import AddDeviceDialog, ConnectDialog
from gui.log_widget import EventLogWidget
from gui.panels import ControlPanel, FlowControlPanel, StatsPanel
from simulator.engine import BROADCAST_RECEIVER, Simulator


class MainWindow(QMainWindow):
    """Main application window embedding the simulator and controls."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Network Protocol Simulator")

        self.sim = Simulator()
        self.canvas = TopologyCanvas(self)
        self.control_panel = ControlPanel(self)
        self.flow_panel = FlowControlPanel(self)
        self.stats_panel = StatsPanel(self)
        self.event_log = EventLogWidget(self)

        self._build_ui()
        self._connect_signals()

        NetworkState.get_instance().on_event(self._on_sim_event)

    def _build_ui(self) -> None:
        """Build the main layout and toolbar."""
        toolbar = QToolBar("Main", self)
        self.addToolBar(toolbar)

        act_add = QAction("+ Add Device", self)
        act_add.triggered.connect(self._on_add_device)
        toolbar.addAction(act_add)

        act_connect = QAction("+ Connect", self)
        act_connect.triggered.connect(self._on_connect)
        toolbar.addAction(act_connect)

        self.scenario_combo = QComboBox(self)
        self.scenario_combo.addItems(
            ["Scenario 1a", "Scenario 1b", "Scenario 2a", "Scenario 2b"]
        )
        toolbar.addWidget(self.scenario_combo)

        act_load = QAction("Load", self)
        act_load.triggered.connect(self._on_load_selected_scenario)
        toolbar.addAction(act_load)

        act_reset = QAction("Reset", self)
        act_reset.triggered.connect(self._on_reset)
        toolbar.addAction(act_reset)

        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.addWidget(self.canvas, stretch=3)

        right = QVBoxLayout()
        right.addWidget(self.control_panel)
        right.addWidget(self.flow_panel)
        right.addWidget(self.stats_panel)
        right.addWidget(self.event_log, stretch=1)
        main_layout.addLayout(right, stretch=2)

        self.setStatusBar(QStatusBar(self))

    def _connect_signals(self) -> None:
        """Wire child widget signals to simulator methods."""
        self.control_panel.send_requested.connect(self._on_send_frame)
        self.flow_panel.flow_requested.connect(self._on_flow_control)

    def _refresh_device_lists(self) -> None:
        names = [
            name
            for name, dev in self.sim.state.devices.items()
            if dev.__class__.__name__ == "EndDevice"
        ]
        self.control_panel.refresh_devices(names)

    def _on_add_device(self) -> None:
        """Show AddDeviceDialog and create the device."""
        dlg = AddDeviceDialog(self)
        if dlg.exec_() != dlg.Accepted:
            return
        name, dtype, mac = dlg.get_values()
        if not name:
            return
        if dtype == "EndDevice":
            if not mac:
                QMessageBox.warning(self, "MAC required", "EndDevice requires a MAC.")
                return
            self.sim.add_device(name, mac)
            self.canvas.add_node(name, "enddevice")
        elif dtype == "Hub":
            self.sim.add_hub(name)
            self.canvas.add_node(name, "hub")
        elif dtype == "Switch":
            self.sim.add_switch(name)
            self.canvas.add_node(name, "switch")
        elif dtype == "Bridge":
            self.sim.add_bridge(name)
            self.canvas.add_node(name, "bridge")
        self._refresh_device_lists()

    def _on_connect(self) -> None:
        """Show ConnectDialog and connect selected devices."""
        devices = list(self.sim.state.devices.keys())
        if len(devices) < 2:
            return
        dlg = ConnectDialog(devices, self)
        if dlg.exec_() != dlg.Accepted:
            return
        a, b, segment = dlg.get_values()
        if self.sim.connect(a, b, segment=segment):
            self.canvas.add_edge(a, b)
        self._update_stats()

    def _on_send_frame(
        self,
        sender: str,
        receiver: str,
        data: str,
        crc: bool,
        csma: bool,
        error: bool,
    ) -> None:
        """Handle send_requested from the ControlPanel."""
        if not sender or not receiver or not data:
            return
        self.sim.send_frame(sender, receiver, data, crc, csma, error)
        self._update_stats()

    def _on_flow_control(
        self,
        protocol: str,
        frames: List[str],
        window: int,
        error_at: int,
    ) -> None:
        """Handle flow control requests from the FlowControlPanel."""
        if not frames:
            return
        if protocol == "Go-Back-N":
            self.sim.run_go_back_n(frames, window, error_at)
        else:
            self.sim.run_selective_repeat(frames, window, error_at)

    def _on_sim_event(self, entry: EventLog) -> None:
        """Callback from NetworkState when new events are logged."""
        self.event_log.append_event(entry)

    def _update_stats(self) -> None:
        """Refresh domain and MAC table reports in the stats panel."""
        self.stats_panel.show_domain_report(self.sim.get_domain_report())
        self.stats_panel.show_mac_table(self.sim.get_mac_table_report())

    def _on_load_selected_scenario(self) -> None:
        """Load the currently selected scenario."""
        label = self.scenario_combo.currentText()
        if label == "Scenario 1a":
            self._scenario_1a()
        elif label == "Scenario 1b":
            self._scenario_1b()
        elif label == "Scenario 2a":
            self._scenario_2a()
        elif label == "Scenario 2b":
            self._scenario_2b()

    def _on_reset(self) -> None:
        """Reset the simulator and canvas."""
        self.sim.reset()
        self.canvas.clear_all()
        self.event_log.clear()
        self._refresh_device_lists()
        self._update_stats()

    # Scenario implementations (simplified, headless engine handles logging)

    def _scenario_1a(self) -> None:
        self._on_reset()
        pc1 = self.sim.add_device("PC1", "AA:BB:CC:00:00:01")
        pc2 = self.sim.add_device("PC2", "AA:BB:CC:00:00:02")
        self.canvas.add_node("PC1", "enddevice")
        self.canvas.add_node("PC2", "enddevice")
        self.sim.connect("PC1", "PC2")
        self.canvas.add_edge("PC1", "PC2")
        self._refresh_device_lists()
        self.sim.send_frame("PC1", "PC2", "Hello PC2!", True, False, False)
        self._update_stats()

    def _scenario_1b(self) -> None:
        self._on_reset()
        hub = self.sim.add_hub("Hub1")
        self.canvas.add_node("Hub1", "hub")
        for i in range(1, 6):
            name = f"PC{i}"
            mac = f"AA:BB:CC:00:01:0{i}"
            self.sim.add_device(name, mac)
            self.canvas.add_node(name, "enddevice")
            self.sim.connect(name, "Hub1")
            self.canvas.add_edge(name, "Hub1")
        self._refresh_device_lists()
        self.sim.send_frame("PC1", BROADCAST_RECEIVER, "Hello everyone!", True, False, False)
        self.statusBar().showMessage("1 collision domain, 1 broadcast domain")
        self._update_stats()

    def _scenario_2a(self) -> None:
        self._on_reset()
        self.sim.add_switch("SW1")
        self.canvas.add_node("SW1", "switch")
        for i in range(1, 6):
            name = f"PC{i}"
            mac = f"AA:BB:CC:00:02:0{i}"
            self.sim.add_device(name, mac)
            self.canvas.add_node(name, "enddevice")
            self.sim.connect(name, "SW1")
            self.canvas.add_edge(name, "SW1")
        self._refresh_device_lists()
        self.sim.send_frame("PC1", "PC3", "Hello PC3", True, False, False)
        self.sim.send_frame("PC2", "PC4", "Hello PC4", True, False, False)
        self.statusBar().showMessage("5 collision domains, 1 broadcast domain")
        self._update_stats()

    def _scenario_2b(self) -> None:
        self._on_reset()
        self.sim.add_switch("SW1")
        self.canvas.add_node("SW1", "switch")
        self.sim.add_hub("Hub1")
        self.sim.add_hub("Hub2")
        self.canvas.add_node("Hub1", "hub")
        self.canvas.add_node("Hub2", "hub")
        self.sim.connect("Hub1", "SW1")
        self.sim.connect("Hub2", "SW1")
        self.canvas.add_edge("Hub1", "SW1")
        self.canvas.add_edge("Hub2", "SW1")
        for i in range(1, 6):
            name = f"PC{i}"
            mac = f"AA:BB:CC:00:03:0{i}"
            self.sim.add_device(name, mac)
            self.canvas.add_node(name, "enddevice")
            self.sim.connect(name, "Hub1")
            self.canvas.add_edge(name, "Hub1")
        for i in range(6, 11):
            name = f"PC{i}"
            mac = f"AA:BB:CC:00:03:{i:02d}"
            self.sim.add_device(name, mac)
            self.canvas.add_node(name, "enddevice")
            self.sim.connect(name, "Hub2")
            self.canvas.add_edge(name, "Hub2")
        self._refresh_device_lists()
        self.sim.send_frame("PC1", "PC8", "Hello PC8", True, False, False)
        self.sim.send_frame("PC10", "PC3", "Hello PC3", True, False, False)
        self.statusBar().showMessage("3 collision domains, 1 broadcast domain")
        self._update_stats()


def launch_gui() -> None:
    """Launch the Qt application main loop."""
    import sys

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

