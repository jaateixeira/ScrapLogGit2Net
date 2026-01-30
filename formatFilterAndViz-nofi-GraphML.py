#! /usr/bin/env python3

# formats and visualizes a graphml file
# filters by organizational affiliation
# layout can be circular or spring (default)
# colorize accourding to affiliation atribute
# nodesize according centralities 

#Example of use verbose,fitering and only top firms with legend
# ./formatFilterAndViz-nofi-GraphML.py  -svtfl test-data/TensorFlow/icis-2024-wp-networks-graphML/tensorFlowGitLog-2015-git-log-outpuyt-by-Jose.IN.NetworkFile.graphML 


######################### How it works ##########################################
#  
# 1- Loads the networks as a networkX object
# 2- Data-cleasing 
# 3- Filtering by org mode (  --org_list_to_ignore args)
# 4- Removing nodes that are not affiliated with organizations in the given list -- args.org_list_only
# 5- Removing nodes that are not affiliated with organizations in the given list or do not collaborate with them (i.e., neighbours)
# 6- Calculates nodes centralities
# 7- Shows/plots and saves the network

#################################################################################


# !/usr/bin/env python3
"""
Formats and visualizes a GraphML file, filters by organizational affiliation,
with configurable layout, coloring, and node sizing.
"""

import argparse
import json
import os
import sys
import random
import configparser
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# For logging
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback
from rich.table import Table
from rich.panel import Panel

# Configure Rich traceback
install_rich_traceback(
    show_locals=True,
    locals_max_length=10,
    locals_max_string=80,
    locals_hide_dunder=True,
    locals_hide_sunder=False,
    indent_guides=True,
    max_frames=5,
    width=100,
    extra_lines=3,
    theme="solarized-dark",
    word_wrap=True,
)

# Initialize console
console = Console()

# Configure logger with Rich handler
logger.remove()
logger.add(
    RichHandler(console=console, show_time=False, show_path=False, rich_tracebacks=True),
    format="{message}",
    level="INFO",
)


@dataclass
class VisualizationConfig:
    """Configuration for GraphML visualization and filtering."""
    input_file: str
    color_map_file: Optional[str] = None
    network_layout: str = "spring"
    node_sizing_strategy: str = "centrality-score"
    node_coloring_strategy: str = "random-color-to-unknown-firms"
    org_list_to_ignore: Optional[List[str]] = None
    org_list_only: Optional[List[str]] = None
    org_list_and_neighbours_only: Optional[List[str]] = None
    org_list_top_only: Optional[str] = None
    org_list_in_config_file: Optional[str] = None
    affiliation_alias_in_config_file: Optional[str] = None
    legend: bool = False
    legend_location: str = "outside_center_right"
    legend_type: str = "top10"
    legend_extra_organizations: Optional[List[str]] = None
    plot: bool = False
    save_graphml: bool = False
    verbose: bool = False
    github_token: Optional[str] = None


class GraphMLVisualizer:
    """Handles GraphML visualization with filtering and customization."""

    def __init__(self, config: VisualizationConfig):
        self.config = config
        self.graph: Optional[nx.Graph] = None
        self.filtered_graph: Optional[nx.Graph] = None
        self.color_map: Dict[str, Any] = {}
        self.degree_centrality: Dict[str, float] = {}
        self.pos: Dict[str, Tuple[float, float]] = {}
        self.affiliation_counts: Dict[str, int] = {}
        self.top_organizations: Dict[str, int] = {}
        self.initial_stats: Dict[str, int] = {}

    def load_graph(self) -> None:
        """Load GraphML file with error handling."""
        console.print(f"[bold cyan]Loading GraphML file:[/bold cyan] {self.config.input_file}")

        try:
            self.graph = nx.read_graphml(self.config.input_file)
            console.print("[green]✓ Graph imported successfully[/green]")
        except Exception as e:
            logger.error(f"Failed to load GraphML file: {e}")
            raise

        # Store initial statistics
        self.initial_stats = {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'isolates': nx.number_of_isolates(self.graph),
        }

        self._print_initial_stats()

    def _print_initial_stats(self) -> None:
        """Print initial graph statistics."""
        stats_panel = Panel.fit(
            f"[bold]Nodes:[/bold] {self.initial_stats['nodes']}\n"
            f"[bold]Edges:[/bold] {self.initial_stats['edges']}\n"
            f"[bold]Isolates:[/bold] {self.initial_stats['isolates']}",
            title="Initial Graph Statistics",
            border_style="blue"
        )
        console.print(stats_panel)

    def load_color_map(self) -> None:
        """Load color map from JSON file or initialize empty."""
        if self.config.color_map_file:
            try:
                with open(self.config.color_map_file, 'r') as file:
                    self.color_map = json.load(file)
                console.print(f"[green]✓ Loaded color map from {self.config.color_map_file}[/green]")
            except FileNotFoundError:
                logger.warning(f"Color map file not found: {self.config.color_map_file}")
                self.color_map = {}
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in color map file: {self.config.color_map_file}")
                self.color_map = {}
        else:
            self.color_map = {}
            console.print("[yellow]No color map provided, using random colors for unknown firms[/yellow]")

    def apply_affiliation_aliases(self) -> None:
        """Apply affiliation aliases from config file."""
        if not self.config.affiliation_alias_in_config_file or not self.graph:
            return

        try:
            config = configparser.ConfigParser()
            config.read(self.config.affiliation_alias_in_config_file)

            if 'aliases' in config:
                aliases = dict(config['aliases'])
                console.print(f"[cyan]Applying {len(aliases)} affiliation aliases[/cyan]")

                for node, data in self.graph.nodes(data=True):
                    affiliation = data.get('affiliation', '')
                    if affiliation in aliases:
                        # Special handling for specific cases
                        if affiliation == "jp":
                            email = data.get('e-mail', '').lower()
                            if "adit" in email:
                                data['affiliation'] = "ADIT"
                            elif "panasonic" in email:
                                data['affiliation'] = "Panasonic"
                            elif "fujitsu" in email:
                                data['affiliation'] = "Fujitsu"
                            else:
                                logger.warning(f"Unhandled 'jp' affiliation for email: {email}")
                        else:
                            data['affiliation'] = aliases[affiliation]

                console.print("[green]✓ Affiliation aliases applied[/green]")
        except Exception as e:
            logger.error(f"Failed to apply affiliation aliases: {e}")

    def normalize_affiliations(self) -> None:
        """Normalize common affiliation patterns."""
        if not self.graph:
            return

        normalized_count = 0
        for _, data in self.graph.nodes(data=True):
            affiliation = data.get('affiliation', '')

            # Normalize 'alum' to 'alum.mit.edu'
            if affiliation == 'alum':
                data['affiliation'] = 'alum.mit.edu'
                normalized_count += 1
                if self.config.verbose:
                    logger.debug(f"Normalized affiliation: alum -> alum.mit.edu")

        if normalized_count > 0:
            console.print(f"[yellow]Normalized {normalized_count} affiliations[/yellow]")

    def analyze_affiliations(self) -> None:
        """Count affiliations in the graph."""
        if not self.graph:
            return

        self.affiliation_counts = {}
        for _, data in self.graph.nodes(data=True):
            affiliation = data.get('affiliation', '')
            if affiliation:
                self.affiliation_counts[affiliation] = self.affiliation_counts.get(affiliation, 0) + 1

        # Sort by count descending
        self.affiliation_counts = dict(
            sorted(self.affiliation_counts.items(), key=lambda x: x[1], reverse=True)
        )

        # Determine top organizations based on config
        if self.config.org_list_top_only:
            n = int(self.config.org_list_top_only.replace('top', ''))
            self.top_organizations = dict(list(self.affiliation_counts.items())[:n])
        else:
            self.top_organizations = dict(list(self.affiliation_counts.items())[:10])  # Default top 10

        self._print_top_organizations()

    def _print_top_organizations(self) -> None:
        """Print top organizations table."""
        if not self.affiliation_counts:
            return

        console.print("\n[bold cyan]Top Organizations by Node Count:[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="dim")
        table.add_column("Organization", style="green")
        table.add_column("Node Count", style="yellow")
        table.add_column("Percentage", style="cyan")

        total_nodes = len(self.graph.nodes()) if self.graph else 0
        for i, (org, count) in enumerate(list(self.affiliation_counts.items())[:20], 1):
            percentage = (count / total_nodes * 100) if total_nodes > 0 else 0
            table.add_row(str(i), org, str(count), f"{percentage:.1f}%")

        console.print(table)

    def filter_graph(self) -> None:
        """Apply all configured filters to the graph."""
        if not self.graph:
            return

        console.print("[bold cyan]Applying filters...[/bold cyan]")
        self.filtered_graph = self.graph.copy()

        # Apply ignore list
        if self.config.org_list_to_ignore:
            self._filter_by_organizations(self.config.org_list_to_ignore, keep=False)

        # Apply only list
        if self.config.org_list_only:
            self._filter_by_organizations(self.config.org_list_only, keep=True)

        # Apply neighbours filter
        if self.config.org_list_and_neighbours_only:
            self._filter_by_organizations_and_neighbours(self.config.org_list_and_neighbours_only)

        # Apply top organizations filter
        if self.config.org_list_top_only:
            self._filter_top_organizations()

        self._print_filtering_results()

    def _filter_by_organizations(self, org_list: List[str], keep: bool = True) -> None:
        """Filter nodes by organization list."""
        if not self.filtered_graph:
            return

        operation = "Keeping only" if keep else "Removing"
        console.print(f"[cyan]{operation} organizations: {org_list}[/cyan]")

        nodes_to_remove = []
        for node, data in self.filtered_graph.nodes(data=True):
            affiliation = data.get('affiliation', '')
            should_remove = (affiliation not in org_list) if keep else (affiliation in org_list)

            if should_remove:
                nodes_to_remove.append(node)
                if self.config.verbose:
                    action = "Removing" if not keep else "Filtering out"
                    console.print(f"  {action} node {node} ({affiliation})")

        self.filtered_graph.remove_nodes_from(nodes_to_remove)

    def _filter_by_organizations_and_neighbours(self, org_list: List[str]) -> None:
        """Filter to keep only specified organizations and their neighbours."""
        if not self.filtered_graph:
            return

        console.print(f"[cyan]Keeping organizations and their neighbours: {org_list}[/cyan]")

        nodes_to_keep = set()

        # First, find all nodes from specified organizations
        for node, data in self.filtered_graph.nodes(data=True):
            if data.get('affiliation', '') in org_list:
                nodes_to_keep.add(node)
                # Add all neighbours
                for neighbor in self.filtered_graph.neighbors(node):
                    nodes_to_keep.add(neighbor)

        # Remove nodes not in keep list
        nodes_to_remove = [
            node for node in self.filtered_graph.nodes()
            if node not in nodes_to_keep
        ]

        self.filtered_graph.remove_nodes_from(nodes_to_remove)

        if self.config.verbose:
            console.print(f"  Kept {len(nodes_to_keep)} nodes, removed {len(nodes_to_remove)} nodes")

    def _filter_top_organizations(self) -> None:
        """Filter to keep only top organizations."""
        if not self.filtered_graph or not self.top_organizations:
            return

        console.print(f"[cyan]Keeping top {len(self.top_organizations)} organizations[/cyan]")

        top_orgs = set(self.top_organizations.keys())
        nodes_to_remove = []

        for node, data in self.filtered_graph.nodes(data=True):
            if data.get('affiliation', '') not in top_orgs:
                nodes_to_remove.append(node)

        self.filtered_graph.remove_nodes_from(nodes_to_remove)

        if self.config.verbose:
            console.print(f"  Removed {len(nodes_to_remove)} nodes not in top organizations")

    def _print_filtering_results(self) -> None:
        """Print filtering results."""
        if not self.filtered_graph:
            return

        console.print("\n[bold cyan]Filtering Results:[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Before", style="yellow")
        table.add_column("After", style="green")
        table.add_column("Change", style="dim")

        nodes_before = self.initial_stats['nodes']
        nodes_after = self.filtered_graph.number_of_nodes()
        nodes_change = nodes_after - nodes_before

        edges_before = self.initial_stats['edges']
        edges_after = self.filtered_graph.number_of_edges()
        edges_change = edges_after - edges_before

        isolates_before = self.initial_stats['isolates']
        isolates_after = nx.number_of_isolates(self.filtered_graph)
        isolates_change = isolates_after - isolates_before

        table.add_row("Nodes", str(nodes_before), str(nodes_after), f"{nodes_change:+d}")
        table.add_row("Edges", str(edges_before), str(edges_after), f"{edges_change:+d}")
        table.add_row("Isolates", str(isolates_before), str(isolates_after), f"{isolates_change:+d}")

        console.print(table)

        # Check for empty graph
        if nodes_after == 0:
            console.print("[bold red]ERROR: Graph is empty after filtering![/bold red]")
            sys.exit(1)

    def calculate_centralities(self) -> None:
        """Calculate centrality measures."""
        if not self.filtered_graph:
            return

        console.print("[bold cyan]Calculating centrality measures...[/bold cyan]")

        try:
            self.degree_centrality = nx.degree_centrality(self.filtered_graph)

            # Print top connected individuals
            sorted_centrality = sorted(
                self.degree_centrality.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            if sorted_centrality:
                console.print("\n[bold]Top 10 Most Connected Individuals:[/bold]")
                for i, (node_id, centrality) in enumerate(sorted_centrality, 1):
                    data = self.filtered_graph.nodes[node_id]
                    email = data.get('e-mail', 'N/A')
                    affiliation = data.get('affiliation', 'unknown')
                    console.print(f"  {i:2}. {email} ({affiliation}): {centrality:.4f}")

        except Exception as e:
            logger.error(f"Error calculating centralities: {e}")
            self.degree_centrality = {}

    def get_node_colors(self) -> List[Any]:
        """Get colors for all nodes based on coloring strategy."""
        if not self.filtered_graph:
            return []

        colors = []
        strategy = self.config.node_coloring_strategy

        for _, data in self.filtered_graph.nodes(data=True):
            affiliation = data.get('affiliation', '')

            if affiliation in self.color_map:
                colors.append(self.color_map[affiliation])
            else:
                if strategy == 'gray-color-to-unknown-firms':
                    colors.append('gray')
                    self.color_map[affiliation] = 'gray'
                elif strategy == 'random-color-to-unknown-firms':
                    color = (random.random(), random.random(), random.random())
                    colors.append(color)
                    self.color_map[affiliation] = color
                elif strategy == 'gray-color-to-others-not-in-topn-filter':
                    # Check if in top organizations
                    if affiliation in self.top_organizations:
                        # Assign a color if not in map
                        if affiliation not in self.color_map:
                            self.color_map[affiliation] = (random.random(), random.random(), random.random())
                        colors.append(self.color_map[affiliation])
                    else:
                        colors.append('gray')
                        self.color_map[affiliation] = 'gray'
                else:
                    # Default fallback
                    colors.append('gray')

        if self.config.verbose:
            console.print("\n[bold]Node Colors:[/bold]")
            for i, (node, data) in enumerate(self.filtered_graph.nodes(data=True)):
                if i < 10:  # Show first 10 only
                    affiliation = data.get('affiliation', 'unknown')
                    color = colors[i]
                    console.print(f"  {affiliation}: {color}")

        return colors

    def get_node_sizes(self) -> List[float]:
        """Calculate node sizes based on centrality."""
        if not self.filtered_graph:
            return []

        if self.config.node_sizing_strategy == 'all-equal':
            return [100] * len(self.filtered_graph.nodes())

        # Centrality-based sizing
        if not self.degree_centrality:
            return [100] * len(self.filtered_graph.nodes())

        return [v * 100 for v in self.degree_centrality.values()]

    def calculate_layout(self) -> None:
        """Calculate node positions based on layout algorithm."""
        if not self.filtered_graph:
            return

        console.print(f"[cyan]Calculating {self.config.network_layout} layout...[/cyan]")

        if self.config.network_layout == 'circular':
            self.pos = nx.circular_layout(self.filtered_graph)
        elif self.config.network_layout == 'spring':
            self.pos = nx.spring_layout(self.filtered_graph)
        else:
            console.print(f"[yellow]Unknown layout, using spring layout[/yellow]")
            self.pos = nx.spring_layout(self.filtered_graph)

    def create_visualization(self) -> None:
        """Create and display/save the visualization."""
        if not self.filtered_graph or not self.pos:
            return

        console.print("[bold cyan]Creating visualization...[/bold cyan]")

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8), facecolor='0.9')

        # Get visualization parameters
        node_colors = self.get_node_colors()
        node_sizes = self.get_node_sizes()

        # Draw nodes
        nx.draw_networkx_nodes(
            self.filtered_graph,
            self.pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8,
            ax=ax
        )

        # Draw edges
        nx.draw_networkx_edges(
            self.filtered_graph,
            self.pos,
            width=0.5,
            alpha=0.5,
            ax=ax
        )

        # Draw labels (only for top nodes if verbose)
        if self.config.verbose:
            labels = {}
            for node in self.filtered_graph.nodes():
                data = self.filtered_graph.nodes[node]
                email = data.get('e-mail', '')
                # Show only first part of email
                if '@' in email:
                    labels[node] = email.split('@')[0]

            nx.draw_networkx_labels(
                self.filtered_graph,
                self.pos,
                labels,
                font_size=8,
                ax=ax
            )

        # Add legend if requested
        if self.config.legend:
            self._add_legend(fig, ax)

        # Configure plot
        ax.set_facecolor('white')
        ax.margins(0.1)
        ax.axis('off')

        # Set title
        title = f"{Path(self.config.input_file).name}\n"
        title += f"Layout: {self.config.network_layout}, "
        title += f"Nodes: {self.filtered_graph.number_of_nodes()}, "
        title += f"Edges: {self.filtered_graph.number_of_edges()}"

        plt.title(title, fontsize=10, pad=20)
        plt.tight_layout()

        # Show or save
        if self.config.plot:
            console.print("[green]Displaying visualization...[/green]")
            plt.show()
        else:
            self._save_visualization(fig)

        plt.close(fig)

    def _add_legend(self, fig, ax) -> None:
        """Add legend to the plot."""
        if not self.affiliation_counts:
            return

        # Create legend elements
        legend_elements = []

        # Determine which organizations to show based on legend type
        if self.config.legend_type == 'top5':
            orgs_to_show = list(self.affiliation_counts.items())[:5]
        elif self.config.legend_type == 'top10':
            orgs_to_show = list(self.affiliation_counts.items())[:10]
        elif self.config.legend_type == 'top20':
            orgs_to_show = list(self.affiliation_counts.items())[:20]
        elif self.config.legend_type.startswith('top10+'):
            orgs_to_show = list(self.affiliation_counts.items())[:10]
            # Add extra organizations if specified
            if self.config.legend_extra_organizations:
                for extra_org in self.config.legend_extra_organizations:
                    if extra_org in self.affiliation_counts:
                        orgs_to_show.append((extra_org, self.affiliation_counts[extra_org]))
        else:
            orgs_to_show = list(self.affiliation_counts.items())[:10]

        # Create legend items
        for org, count in orgs_to_show:
            color = self.color_map.get(org, 'gray')
            legend_elements.append(
                Line2D(
                    [0], [0],
                    marker='o',
                    color=color,
                    label=f"{org} ({count})",
                    lw=0,
                    markerfacecolor=color,
                    markersize=8
                )
            )

        # Position legend based on location
        if self.config.legend_location == 'outside_center_right':
            fig.subplots_adjust(right=0.7)
            ax.legend(
                handles=legend_elements,
                loc='center left',
                bbox_to_anchor=(1.05, 0.5),
                frameon=False,
                prop={'size': 9}
            )
        elif self.config.legend_location == 'upper_right':
            ax.legend(
                handles=legend_elements,
                loc='upper right',
                frameon=False,
                prop={'size': 8}
            )
        elif self.config.legend_location == 'lower_right':
            ax.legend(
                handles=legend_elements,
                loc='lower right',
                frameon=False,
                prop={'size': 8}
            )
        else:  # Default to center right
            ax.legend(
                handles=legend_elements,
                loc='center right',
                frameon=False,
                prop={'size': 9}
            )

    def _save_visualization(self, fig) -> None:
        """Save visualization to files."""
        base_name = Path(self.config.input_file).stem
        layout = self.config.network_layout

        # Save as PNG
        png_file = f"{base_name}_{layout}.png"
        fig.savefig(png_file, dpi=300, bbox_inches='tight')
        console.print(f"[green]✓ Saved PNG: {png_file}[/green]")

        # Save as PDF
        pdf_file = f"{base_name}_{layout}.pdf"
        fig.savefig(pdf_file, bbox_inches='tight')
        console.print(f"[green]✓ Saved PDF: {pdf_file}[/green]")

    def save_filtered_graphml(self) -> None:
        """Save filtered graph as GraphML file."""
        if not self.filtered_graph or not self.config.save_graphml:
            return

        console.print("[bold cyan]Saving filtered GraphML...[/bold cyan]")

        base_name = Path(self.config.input_file).stem
        output_file = f"{base_name}_filtered.graphml"

        # Handle duplicate filenames
        counter = 1
        while Path(output_file).exists():
            output_file = f"{base_name}_filtered_{counter}.graphml"
            counter += 1

        try:
            nx.write_graphml(self.filtered_graph, output_file)
            console.print(f"[green]✓ Saved filtered GraphML: {output_file}[/green]")

            # Print filtered graph stats
            stats_panel = Panel.fit(
                f"[bold]Nodes:[/bold] {self.filtered_graph.number_of_nodes()}\n"
                f"[bold]Edges:[/bold] {self.filtered_graph.number_of_edges()}\n"
                f"[bold]Isolates:[/bold] {nx.number_of_isolates(self.filtered_graph)}",
                title="Filtered Graph Statistics",
                border_style="green"
            )
            console.print(stats_panel)

        except Exception as e:
            logger.error(f"Failed to save GraphML file: {e}")


def parse_arguments() -> VisualizationConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="formatFilterAndViz-nofi-GraphML.py",
        description="Formats and visualizes a GraphML file with organizational filtering"
    )

    parser.add_argument(
        "infile",
        nargs='?',
        type=str,
        help="The network file (created by ScrapLogGit2Net)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity"
    )

    parser.add_argument(
        "-c", "--color-map",
        type=str,
        dest="color_map_file",
        help="JSON file mapping organizations to colors"
    )

    parser.add_argument(
        "-nl", "--network-layout",
        choices=['circular', 'spring'],
        default='spring',
        help="Network layout algorithm"
    )

    parser.add_argument(
        "-ns", "--node-sizing-strategy",
        choices=['all-equal', 'centrality-score'],
        default='centrality-score',
        help="Node sizing strategy"
    )

    parser.add_argument(
        "-nc", "--node-coloring-strategy",
        choices=[
            'random-color-to-unknown-firms',
            'gray-color-to-unknown-firms',
            'gray-color-to-others-not-in-topn-filter'
        ],
        default='random-color-to-unknown-firms',
        help="Node coloring strategy"
    )

    parser.add_argument(
        "-oi", "--org-list-to-ignore",
        type=lambda s: [item.strip() for item in s.split(',')],
        help="Filter out developers affiliated with organizations in a given list (comma-separated)"
    )

    parser.add_argument(
        "-oo", "--org-list-only",
        type=lambda s: [item.strip() for item in s.split(',')],
        help="Consider only developers affiliated with organizations in a given list (comma-separated)"
    )

    parser.add_argument(
        "-on", "--org-list-and-neighbours-only",
        type=lambda s: [item.strip() for item in s.split(',')],
        help="Consider only organizations in a given list and their neighbours"
    )

    parser.add_argument(
        "-ot", "--org-list-top-only",
        choices=['top5', 'top10', 'top20'],
        help="Consider only top organizations by node count"
    )

    parser.add_argument(
        "-a", "--affiliation-alias-in-config-file",
        type=str,
        help="Configuration file for email domain aliases"
    )

    parser.add_argument(
        "-p", "--plot",
        action="store_true",
        help="Display visualization instead of saving"
    )

    parser.add_argument(
        "-l", "--legend",
        action="store_true",
        help="Show legend in visualization"
    )

    parser.add_argument(
        "-ll", "--legend-location",
        choices=[
            'upper_right', 'upper_left',
            'center_right', 'center_left',
            'lower_right', 'lower_left',
            'outside_center_right'
        ],
        default='outside_center_right',
        help="Legend location"
    )

    parser.add_argument(
        "-lt", "--legend-type",
        choices=['top5', 'top10', 'top20', 'top10+1', 'top10+others'],
        default='top10',
        help="Type of legend to display"
    )

    parser.add_argument(
        "-le", "--legend-extra-organizations",
        type=lambda s: [item.strip() for item in s.split(',')],
        help="Extra organizations to include in legend (comma-separated)"
    )

    parser.add_argument(
        "-s", "--save-graphml",
        action="store_true",
        help="Save filtered graph as new GraphML file"
    )

    parser.add_argument(
        "-g", "--github",
        type=str,
        dest="github_token",
        help="GitHub API token for affiliation resolution (not implemented)"
    )

    args = parser.parse_args()

    # Handle file input via dialog if not provided
    if not args.infile:
        console.print("[yellow]No input file provided, opening file dialog...[/yellow]")
        root = tk.Tk()
        root.withdraw()
        input_file = filedialog.askopenfilename(
            title="Select GraphML file",
            filetypes=[("GraphML files", "*.graphml"), ("All files", "*.*")]
        )
        root.destroy()

        if not input_file:
            console.print("[red]No file selected. Exiting.[/red]")
            sys.exit(1)

        args.infile = input_file

    # Validate input file
    if not Path(args.infile).is_file():
        console.print(f"[red]File not found: {args.infile}[/red]")
        sys.exit(1)

    return VisualizationConfig(
        input_file=args.infile,
        color_map_file=args.color_map_file,
        network_layout=args.network_layout,
        node_sizing_strategy=args.node_sizing_strategy,
        node_coloring_strategy=args.node_coloring_strategy,
        org_list_to_ignore=args.org_list_to_ignore,
        org_list_only=args.org_list_only,
        org_list_and_neighbours_only=args.org_list_and_neighbours_only,
        org_list_top_only=args.org_list_top_only,
        affiliation_alias_in_config_file=args.affiliation_alias_in_config_file,
        legend=args.legend,
        legend_location=args.legend_location,
        legend_type=args.legend_type,
        legend_extra_organizations=args.legend_extra_organizations,
        plot=args.plot,
        save_graphml=args.save_graphml,
        verbose=args.verbose,
        github_token=args.github_token,
    )


def print_banner() -> None:
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║          formatFilterAndViz-nofi-GraphML.py                  ║
║     GraphML Visualization with Organizational Filtering      ║
╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner)


def main() -> None:
    """Main function to orchestrate the GraphML visualization."""
    print_banner()

    try:
        # Parse arguments
        config = parse_arguments()

        # Set log level based on verbosity
        if config.verbose:
            logger.remove()
            logger.add(
                RichHandler(console=console, show_time=True, show_path=True, rich_tracebacks=True),
                format="{message}",
                level="DEBUG",
            )

        # Create visualizer
        visualizer = GraphMLVisualizer(config)

        # Load and process graph
        visualizer.load_graph()
        visualizer.load_color_map()
        visualizer.apply_affiliation_aliases()
        visualizer.normalize_affiliations()
        visualizer.analyze_affiliations()
        visualizer.filter_graph()
        visualizer.calculate_centralities()
        visualizer.calculate_layout()

        # Create visualization
        visualizer.create_visualization()

        # Save filtered graph if requested
        if config.save_graphml:
            visualizer.save_filtered_graphml()

        console.print("\n✅ [bold green]Visualization completed successfully![/bold green]")

    except FileNotFoundError as e:
        console.print(f"\n❌ [bold red]File not found:[/bold red] {e}")
        sys.exit(1)
    except nx.NetworkXError as e:
        console.print(f"\n❌ [bold red]NetworkX error:[/bold red] {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"\n❌ [bold red]Invalid JSON in color map:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ [bold red]Unexpected error:[/bold red] {e}")
        if config.verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()