#!/usr/bin/env python3
"""
Formats and visualizes a graphML file capturing a weighted Network of Organizations created by ScrapLog.
Edges thickness maps its weight, nodes are colorized according to affiliation attribute.
"""

import sys
import os
import json
import math
import random
import argparse
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


from utils.unified_logger import logger
from utils.unified_console import Console
from utils.unified_console import rprint


@dataclass
class NetworkConfig:
    """Configuration for network visualization."""
    input_file: str
    network_layout: str = "spring"
    node_sizing_strategy: str = "centrality-score"
    node_coloring_strategy: str = "random-color-to-unknown-firms"
    focal_firm: Optional[str] = None
    color_map_file: Optional[str] = None
    show_visualization: bool = False
    show_legend: bool = False
    verbose: bool = False
    top_firms_only: bool = False
    filter_by_org: bool = False


class NetworkVisualizer:
    """Handles network visualization with various customization options."""

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.graph: Optional[nx.Graph] = None
        self.pos: Optional[Dict[str, Tuple[float, float]]] = None
        self.known_org_node_colors: Dict[str, Any] = {}
        self.degree_centrality: Optional[Dict[str, float]] = None

    def load_graph(self) -> None:
        """Load GraphML file."""
        logger.info(f"Loading network from {self.config.input_file}")
        self.graph = nx.read_graphml(self.config.input_file)

        logger.info(f"Number of nodes: {self.graph.number_of_nodes()}")
        logger.info(f"Number of edges: {self.graph.number_of_edges()}")
        logger.info(f"Number of isolates: {nx.number_of_isolates(self.graph)}")

        if self.config.verbose:
            self._print_graph_details()

    def _print_graph_details(self) -> None:
        """Print detailed graph information (verbose mode only)."""
        if not self.graph:
            return

        logger.debug("Graph as dict of dicts:")
        logger.debug(nx.to_dict_of_dicts(self.graph))

        logger.debug("Nodes and their data:")
        for node, data in self.graph.nodes(data=True):
            logger.debug(f"\t{node}: {data}")

        logger.debug("Edges and their data:")
        for edge in self.graph.edges(data=True):
            logger.debug(f"\t{edge}")

    def calculate_centralities(self) -> None:
        """Calculate network centralities."""
        logger.info("Calculating centralities...")
        if not self.graph:
            raise ValueError("Graph not loaded")

        self.degree_centrality = nx.eigenvector_centrality(self.graph)
        sorted_centrality = sorted(
            self.degree_centrality.items(),
            key=lambda item: item[1],
            reverse=True
        )

        if self.config.verbose:
            logger.debug("Top 10 central nodes:")
            for node, centrality in sorted_centrality[:10]:
                logger.debug(f"\t{node}: {centrality:.4f}")

    def load_color_map(self) -> None:
        """Load color map from JSON file or initialize empty."""
        if self.config.color_map_file:
            try:
                with open(self.config.color_map_file, 'r') as file:
                    self.known_org_node_colors = json.load(file)
                logger.info(f"Loaded color map from {self.config.color_map_file}")
            except FileNotFoundError:
                logger.warning(f"Color map file not found: {self.config.color_map_file}")
                self.known_org_node_colors = {}
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in color map file: {self.config.color_map_file}")
                self.known_org_node_colors = {}
        else:
            self.known_org_node_colors = {}
            logger.info("No color map provided, using random colors for unknown firms")

    def get_node_colors(self) -> List[Any]:
        """Get colors for all nodes based on coloring strategy."""
        if not self.graph:
            return []

        colors = []
        strategy = self.config.node_coloring_strategy

        for node in self.graph.nodes():
            if node in self.known_org_node_colors:
                colors.append(self.known_org_node_colors[node])
            else:
                if strategy == 'gray-color-to-unknown-firms':
                    color = 'gray'
                elif strategy == 'random-color-to-unknown-firms':
                    color = (random.random(), random.random(), random.random())
                else:
                    logger.error(f"Unknown coloring strategy: {strategy}")
                    color = 'gray'

                colors.append(color)
                self.known_org_node_colors[node] = color

        if self.config.verbose:
            logger.debug("Node colors:")
            for node, color in zip(self.graph.nodes(), colors):
                logger.debug(f"\t{node}: {color}")

        return colors

    def get_node_sizes(self) -> List[float]:
        """Calculate node sizes based on centrality."""
        if not self.degree_centrality or not self.graph:
            return [100] * self.graph.number_of_nodes()

        if self.config.node_sizing_strategy == 'all-equal':
            return [100] * self.graph.number_of_nodes()

        # Centrality-based sizing
        custom_factor = 20
        return [v * custom_factor * 100 for v in self.degree_centrality.values()]

    def get_edge_thickness(self) -> List[float]:
        """Calculate edge thickness based on weights."""
        if not self.graph:
            return []

        thickness = []
        for _, _, edge_data in self.graph.edges(data=True):
            weight = edge_data.get('weight', 1)
            # Use log base 2 to scale thickness
            thickness.append(1 + math.log(weight, 2))

        return thickness

    def get_layout_positions(self) -> Dict[str, Tuple[float, float]]:
        """Calculate node positions based on layout algorithm."""
        if not self.graph:
            return {}

        if self.config.network_layout == 'circular':
            return nx.circular_layout(self.graph)
        elif self.config.network_layout == 'spring':
            return nx.spring_layout(self.graph)
        else:
            logger.error(f"Unknown layout: {self.config.network_layout}")
            return nx.spring_layout(self.graph)

    def get_legend_elements(self) -> List[Line2D]:
        """Create legend elements for the plot."""
        elements = []

        for org in self.graph.nodes() if self.graph else []:
            color = self.known_org_node_colors.get(org, 'gray')
            elements.append(
                Line2D(
                    [0], [0],
                    marker='o',
                    color=color,
                    label=org,
                    lw=0,
                    markerfacecolor=color,
                    markersize=5
                )
            )

        return elements

    def add_focal_firm_highlight(self, ax: plt.Axes) -> None:
        """Add a highlight circle around the focal firm."""
        if not self.config.focal_firm or not self.graph:
            return

        if self.config.focal_firm not in self.graph.nodes():
            logger.error(f"Focal firm '{self.config.focal_firm}' not in graph nodes")
            return

        if self.config.focal_firm not in self.pos:
            logger.error(f"Position not calculated for focal firm '{self.config.focal_firm}'")
            return

        custom_radius = 0.10
        highlight_circle = plt.Circle(
            self.pos[self.config.focal_firm],
            custom_radius,
            fill=False,
            alpha=0.5
        )
        ax.add_artist(highlight_circle)

        if self.config.verbose:
            logger.info(f"Focal firm position: {self.pos[self.config.focal_firm]}")

    def visualize(self) -> None:
        """Main visualization method."""
        if not self.graph:
            raise ValueError("Graph not loaded")

        logger.info("Creating visualization...")

        # Calculate positions
        self.pos = self.get_layout_positions()

        # Create figure
        plt.figure(figsize=(12, 10))

        # Get visualization parameters
        node_colors = self.get_node_colors()
        node_sizes = self.get_node_sizes()
        edge_thickness = self.get_edge_thickness()

        # Draw nodes
        node_options = {
            'node_shape': 'o',
            'node_color': node_colors,
            'node_size': node_sizes,
            'alpha': 0.75
        }

        nx.draw_networkx_nodes(self.graph, self.pos, **node_options)

        # Draw edges
        edge_options = {
            'width': edge_thickness,
            'alpha': 0.2
        }
        nx.draw_networkx_edges(self.graph, self.pos, **edge_options)

        # Draw labels
        nx.draw_networkx_labels(
            self.graph,
            self.pos,
            font_size=10,
            font_family="sans-serif",
            font_weight="bold",
            font_color='black',
            alpha=1.0
        )

        # Draw edge labels
        weight_labels = nx.get_edge_attributes(self.graph, name='weight')
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=weight_labels)

        # Add legend if requested
        if self.config.show_legend:
            legend_elements = self.get_legend_elements()
            plt.legend(
                handles=legend_elements,
                loc='center left',
                bbox_to_anchor=(0.95, 0.5),
                frameon=False,
                prop={'weight': 'bold', 'size': 10, 'family': 'sans-serif'}
            )

        # Add focal firm highlight
        ax = plt.gca()
        self.add_focal_firm_highlight(ax)

        # Configure plot
        ax.margins(0.08)
        plt.axis("off")
        plt.tight_layout()

        # Set title from config
        config_str = str(vars(self.config))
        mid_point = (len(config_str) + 1) // 2
        title = f"{config_str[:mid_point]}\n{config_str[mid_point:]}"
        plt.title(title, fontsize=8)

        # Show or save
        if self.config.show_visualization:
            logger.info("Displaying visualization...")
            plt.show()
        else:
            base_name = os.path.splitext(self.config.input_file)[0]
            pdf_path = f"{base_name}-{self.config.network_layout}.pdf"
            png_path = f"{base_name}-{self.config.network_layout}.png"

            logger.info(f"Saving PDF to {pdf_path}")
            plt.savefig(pdf_path, format='pdf', dpi=300, bbox_inches='tight')

            logger.info(f"Saving PNG to {png_path}")
            plt.savefig(png_path, format='png', dpi=300, bbox_inches='tight')

        plt.close()


def parse_arguments() -> NetworkConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="formatAndViz-nofo-GraphML.py",
        description="Formats and visualizes a graphML file capturing a weighted Network of Organizations"
    )

    parser.add_argument("file", type=str, help="The network file (GraphML format)")

    parser.add_argument(
        "-n", "--network_layout",
        choices=['circular', 'spring'],
        default='spring',
        help="Network layout algorithm"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity"
    )

    parser.add_argument(
        "-ns", "--node_sizing_strategy",
        choices=['all-equal', 'centrality-score'],
        default='centrality-score',
        help="Node sizing strategy"
    )

    parser.add_argument(
        "-nc", "--node_coloring_strategy",
        choices=[
            'random-color-to-unknown-firms',
            'gray-color-to-unknown-firms',
            'gray-color-to-others-not-in-topn-filter'
        ],
        default='random-color-to-unknown-firms',
        help="Node coloring strategy"
    )

    parser.add_argument(
        "-c", "--color_map",
        type=str,
        help="JSON file mapping firms to colors"
    )

    parser.add_argument(
        "-ff", "--focal_firm",
        type=str,
        help="Focal firm to highlight"
    )

    parser.add_argument(
        "-t", "--top_firms_only",
        action="store_true",
        help="Only show top firms"
    )

    parser.add_argument(
        "-f", "--filter_by_org",
        action="store_true",
        help="Filter by organization"
    )

    parser.add_argument(
        "-s", "--show",
        action="store_true",
        help="Show visualization instead of saving"
    )

    parser.add_argument(
        "-l", "--legend",
        action="store_true",
        help="Add legend to visualization"
    )

    args = parser.parse_args()

    return NetworkConfig(
        input_file=args.file,
        network_layout=args.network_layout,
        node_sizing_strategy=args.node_sizing_strategy,
        node_coloring_strategy=args.node_coloring_strategy,
        focal_firm=args.focal_firm,
        color_map_file=args.color_map,
        show_visualization=args.show,
        show_legend=args.legend,
        verbose=args.verbose,
        top_firms_only=args.top_firms_only,
        filter_by_org=args.filter_by_org,
    )


def print_banner() -> None:
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║ formatAndViz-nofo-GraphML.py                                 ║
║ Visualizing weighted networks of organizations since June 2024║
╚══════════════════════════════════════════════════════════════╝
    """
    rprint(banner)


def main() -> None:
    """Main function."""
    print_banner()

    try:
        # Parse arguments
        config = parse_arguments()

        # Create visualizer
        visualizer = NetworkVisualizer(config)

        # Load and process graph
        visualizer.load_graph()
        visualizer.calculate_centralities()
        visualizer.load_color_map()

        # Generate visualization
        visualizer.visualize()

        logger.success("Visualization completed successfully!")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        sys.exit(1)
    except nx.NetworkXError as e:
        logger.error(f"NetworkX error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()