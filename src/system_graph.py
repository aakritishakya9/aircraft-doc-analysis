import networkx as nx
import matplotlib.pyplot as plt
import io
from typing import Dict, List, Any

class AircraftSystemKnowledgeGraph:
    """
    Constructs a directed knowledge graph of aircraft ATA chapters,
    subsystems, hydraulic/electrical circuits, and downstream dependencies
    to evaluate multi-system ripple effects when specifications shift.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_subsystem_topology()

    def _build_subsystem_topology(self):
        # Nodes: System components and downstream consumers
        # Hydraulic System Green Loop (ATA 29)
        self.graph.add_node("HYD-001", label="Engine Hydraulic Pump (EDP)\n[ATA 29 - Source]", system="Hydraulic Power", level=0)
        self.graph.add_node("HYD-VALVE", label="System Pressure Relief Valve\n[ATA 29 - Reg]", system="Hydraulic Power", level=1)
        self.graph.add_node("GSE-CART", label="Hydraulic Ground Test Rig\n[GSE Tooling]", system="Tooling", level=1)
        
        # Consumers of Green Hydraulic System
        self.graph.add_node("LG-002", label="Landing Gear Retract Actuator\n[ATA 32 - Consumer]", system="Landing Gear", level=2)
        self.graph.add_node("BRK-003", label="Main Gear Carbon Brakes\n[ATA 32 - Consumer]", system="Landing Gear", level=2)
        self.graph.add_node("FLT-004", label="Elevator Servo Actuator\n[ATA 27 - Consumer]", system="Flight Controls", level=2)
        self.graph.add_node("FLT-005", label="Slats Power Control Unit\n[ATA 27 - Consumer]", system="Flight Controls", level=2)
        self.graph.add_node("DOOR-006", label="Cargo Door Actuator\n[ATA 52 - Consumer]", system="Doors", level=2)

        # Edges with interface descriptions
        self.graph.add_edge("HYD-001", "HYD-VALVE", relation="Relief Calibration (3200 PSI)")
        self.graph.add_edge("HYD-001", "GSE-CART", relation="Bench Coupling & Pressure Matching")
        self.graph.add_edge("HYD-001", "LG-002", relation="Green High-Pressure Supply (Delivery Pressure)")
        self.graph.add_edge("HYD-001", "BRK-003", relation="Normal Braking Fluid Feed")
        self.graph.add_edge("HYD-001", "FLT-004", relation="Pitch Axis Hydraulic Power")
        self.graph.add_edge("HYD-001", "FLT-005", relation="High Lift Slat Motor Drive")
        self.graph.add_edge("HYD-001", "DOOR-006", relation="Ground Door Operation")

    def trace_ripple_effect(self, source_component: str = "HYD-001") -> List[Dict[str, Any]]:
        """
        Returns list of downstream affected systems and their risk level.
        """
        if source_component not in self.graph:
            return []

        downstream_nodes = list(nx.dfs_preorder_nodes(self.graph, source=source_component))
        results = []
        for node in downstream_nodes:
            if node == source_component:
                continue
            node_data = self.graph.nodes[node]
            edge_data = self.graph.get_edge_data(source_component, node) or {}
            relation = edge_data.get("relation", "Downstream fluid/electrical interface")
            
            risk = "CRITICAL" if node in ["HYD-VALVE", "GSE-CART", "LG-002"] else "MEDIUM"
            results.append({
                "subsystem_id": node,
                "subsystem_name": node_data.get("label", node).split("\n")[0],
                "ata_system": node_data.get("system", "General"),
                "interface_coupling": relation,
                "ripple_risk": risk
            })
        return results

    def render_graph_image(self) -> bytes:
        """
        Renders a clean topological graph diagram to PNG bytes using Matplotlib.
        """
        plt.figure(figsize=(10, 6), facecolor="#F8FAFC")
        pos = {
            "HYD-001": (0, 0),
            "HYD-VALVE": (2, 2),
            "GSE-CART": (2, -2),
            "LG-002": (4, 1.5),
            "BRK-003": (4, 0.5),
            "FLT-004": (4, -0.5),
            "FLT-005": (4, -1.5),
            "DOOR-006": (4, -2.5),
        }

        # Colors by subsystem
        node_colors = []
        for n in self.graph.nodes():
            if n == "HYD-001":
                node_colors.append("#DC2626")  # Primary Source (Red)
            elif n in ["HYD-VALVE", "GSE-CART"]:
                node_colors.append("#F59E0B")  # Direct Impact (Amber)
            else:
                node_colors.append("#0284C7")  # Downstream Consumers (Blue)

        nx.draw_networkx_nodes(self.graph, pos, node_size=3200, node_color=node_colors, alpha=0.9)
        nx.draw_networkx_edges(self.graph, pos, width=2, edge_color="#94A3B8", arrows=True, arrowsize=20, min_source_margin=25, min_target_margin=25)
        
        labels = {n: self.graph.nodes[n]["label"] for n in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8, font_family="sans-serif", font_weight="bold", font_color="#0F172A")

        plt.title("Aircraft ATA Subsystem Ripple Effect Topology (ATA 29 Power Source -> Downstream Consumers)", fontsize=11, fontweight="bold", pad=15, color="#002B49")
        plt.axis("off")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        plt.close()
        return buf.getvalue()
