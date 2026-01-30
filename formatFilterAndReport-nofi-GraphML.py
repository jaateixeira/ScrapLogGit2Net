#!/usr/bin/env python3
"""
formatAndReportGraphML - Reporter for GraphML files with comprehensive analysis and reporting.
"""

import argparse
import os
import sys
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

import networkx as nx
import xlwt

from utils.unified_logger import logger
from utils.unified_console import console
from utils.unified_console import Table
from utils.unified_console import Progress


from rich.progress import SpinnerColumn, TextColumn




@dataclass
class ReportConfig:
    """Configuration for GraphML reporting."""
    input_file: str
    org_list_to_ignore: Optional[List[str]] = None
    org_list_only: Optional[List[str]] = None
    color_map_file: Optional[str] = None
    verbose: bool = False
    top_n_organizations: int = 20
    top_n_individuals: int = 10


class GraphMLReporter:
    """Handles GraphML file analysis and reporting."""

    def __init__(self, config: ReportConfig):
        self.config = config
        self.graph: Optional[nx.Graph] = None
        self.color_map: Dict[str, str] = {}
        self.stats: Dict[str, Any] = {}
        self.top_organizations: Dict[str, int] = {}
        self.centralities: List[Tuple[str, float]] = []

    def load_graph(self) -> None:
        """Load and validate GraphML file."""
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("Loading GraphML file...", total=None)

            try:
                self.graph = nx.read_graphml(self.config.input_file)
                progress.update(task, description="✅ GraphML loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load GraphML file: {e}")
                raise

        self._validate_graph()

    def _validate_graph(self) -> None:
        """Validate the loaded graph has required attributes."""
        if not self.graph:
            raise ValueError("Graph not loaded")

        if self.graph.number_of_nodes() == 0:
            logger.warning("Graph has no nodes")

        if self.graph.number_of_edges() == 0:
            logger.warning("Graph has no edges")

    def load_color_map(self) -> None:
        """Load color map from JSON file if provided."""
        if not self.config.color_map_file:
            logger.info("No color map provided")
            return

        try:
            with open(self.config.color_map_file, 'r') as file:
                self.color_map = json.load(file)
            logger.info(f"Loaded color map from {self.config.color_map_file}")
        except FileNotFoundError:
            logger.warning(f"Color map file not found: {self.config.color_map_file}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in color map file: {self.config.color_map_file}")

    def normalize_affiliations(self) -> None:
        """Normalize affiliation domains that represent the same organization."""
        if not self.graph:
            return

        changes_made = False
        for node, data in self.graph.nodes(data=True):
            affiliation = data.get('affiliation', '')

            # Normalize common patterns
            if affiliation == 'alum':
                data['affiliation'] = 'alum.mit.edu'
                changes_made = True
                if self.config.verbose:
                    logger.debug(f"Normalized {node}: alum -> alum.mit.edu")

            # Add more normalization rules as needed
            # Example: cz.ibm.com -> ibm.com

        if changes_made:
            logger.info("Affiliation normalization completed")

    def filter_by_organizations(self) -> None:
        """Filter graph based on organization lists."""
        if not self.graph:
            return

        original_node_count = self.graph.number_of_nodes()

        # Filter out ignored organizations
        if self.config.org_list_to_ignore:
            self._filter_organizations(self.config.org_list_to_ignore, exclude=True)

        # Filter to include only specified organizations
        if self.config.org_list_only:
            self._filter_organizations(self.config.org_list_only, exclude=False)

        filtered_out = original_node_count - self.graph.number_of_nodes()
        if filtered_out > 0:
            logger.info(f"Filtered out {filtered_out} nodes")

    def _filter_organizations(self, org_list: List[str], exclude: bool = True) -> None:
        """Internal method to filter nodes by organization."""
        if not self.graph:
            return

        operation = "Excluding" if exclude else "Including only"
        logger.info(f"{operation} organizations: {org_list}")

        nodes_to_remove = []
        for node, data in self.graph.nodes(data=True):
            affiliation = data.get('affiliation', '')
            should_remove = (affiliation in org_list) if exclude else (affiliation not in org_list)

            if should_remove:
                nodes_to_remove.append(node)
                if self.config.verbose:
                    action = "Removing" if exclude else "Filtering out"
                    logger.debug(f"{action} node {node} ({affiliation})")

        self.graph.remove_nodes_from(nodes_to_remove)

    def calculate_statistics(self) -> None:
        """Calculate comprehensive graph statistics."""
        if not self.graph:
            return

        logger.info("Calculating graph statistics...")

        self.stats = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'num_isolates': nx.number_of_isolates(self.graph),
            'isolates': list(nx.isolates(self.graph)),
            'density': nx.density(self.graph),
            'is_connected': nx.is_connected(self.graph) if self.graph.number_of_nodes() > 0 else False,
        }

        # Calculate components if graph is not connected
        if not self.stats['is_connected']:
            self.stats['connected_components'] = nx.number_connected_components(self.graph)
            self.stats['component_sizes'] = [
                len(c) for c in nx.connected_components(self.graph)
            ]

    def calculate_centralities(self) -> None:
        """Calculate centrality measures for nodes."""
        if not self.graph:
            return

        logger.info("Calculating centrality measures...")

        try:
            degree_centrality = nx.degree_centrality(self.graph)
            self.centralities = sorted(
                degree_centrality.items(),
                key=lambda x: x[1],
                reverse=True
            )[:self.config.top_n_individuals]
        except Exception as e:
            logger.warning(f"Could not calculate centralities: {e}")
            self.centralities = []

    def analyze_organizations(self) -> None:
        """Analyze organizations in the graph."""
        if not self.graph:
            return

        logger.info("Analyzing organizations...")

        affiliations_freq: Dict[str, int] = {}
        for _, data in self.graph.nodes(data=True):
            affiliation = data.get('affiliation', '')
            if affiliation:
                affiliations_freq[affiliation] = affiliations_freq.get(affiliation, 0) + 1

        # Sort by frequency and get top N
        self.top_organizations = dict(
            sorted(
                affiliations_freq.items(),
                key=lambda x: x[1],
                reverse=True
            )[:self.config.top_n_organizations]
        )

    def calculate_edge_analysis(self) -> Dict[str, Any]:
        """Calculate edge analysis by organization."""
        if not self.graph:
            return {}

        logger.info("Analyzing edges by organization...")

        # Count edges within and between organizations
        intra_org_edges = 0
        inter_org_edges = 0
        org_edge_counts: Dict[str, int] = {}

        for u, v in self.graph.edges():
            u_aff = self.graph.nodes[u].get('affiliation', 'unknown')
            v_aff = self.graph.nodes[v].get('affiliation', 'unknown')

            if u_aff == v_aff:
                intra_org_edges += 1
                org_edge_counts[u_aff] = org_edge_counts.get(u_aff, 0) + 1
            else:
                inter_org_edges += 1

        return {
            'intra_organization_edges': intra_org_edges,
            'inter_organization_edges': inter_org_edges,
            'organization_edge_counts': dict(
                sorted(org_edge_counts.items(), key=lambda x: x[1], reverse=True)
            ),
        }

    def print_statistics(self) -> None:
        """Print statistics to console in a formatted way."""
        if not self.stats:
            return

        # Create a table for basic stats
        table = Table(title="Graph Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Number of nodes", str(self.stats['num_nodes']))
        table.add_row("Number of edges", str(self.stats['num_edges']))
        table.add_row("Number of isolates", str(self.stats['num_isolates']))
        table.add_row("Graph density", f"{self.stats['density']:.4f}")
        table.add_row("Is connected", str(self.stats['is_connected']))

        if 'connected_components' in self.stats:
            table.add_row("Connected components", str(self.stats['connected_components']))

        console.print(table)

        # Print isolates if any
        if self.stats['isolates']:
            console.print("\n[bold yellow]Isolated nodes:[/bold yellow]")
            for isolate in self.stats['isolates']:
                data = self.graph.nodes[isolate] if self.graph else {}
                console.print(f"  • {isolate}: {data.get('email', 'N/A')} @ {data.get('affiliation', 'N/A')}")

    def print_organization_analysis(self) -> None:
        """Print organization analysis to console."""
        if not self.top_organizations:
            return

        table = Table(
            title=f"Top {len(self.top_organizations)} Organizations by Node Count",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Rank", style="dim")
        table.add_column("Organization", style="cyan")
        table.add_column("Node Count", style="green")
        table.add_column("Percentage", style="yellow")

        total_nodes = self.stats.get('num_nodes', 0)
        for i, (org, count) in enumerate(self.top_organizations.items(), 1):
            percentage = (count / total_nodes * 100) if total_nodes > 0 else 0
            table.add_row(
                str(i),
                org,
                str(count),
                f"{percentage:.1f}%"
            )

        console.print(table)

    def print_centrality_analysis(self) -> None:
        """Print centrality analysis to console."""
        if not self.centralities:
            console.print("[yellow]No centrality data available[/yellow]")
            return

        table = Table(
            title=f"Top {len(self.centralities)} Individuals by Degree Centrality",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Rank", style="dim")
        table.add_column("Node ID", style="cyan")
        table.add_column("Centrality", style="green")
        table.add_column("Affiliation", style="yellow")

        for i, (node_id, centrality) in enumerate(self.centralities, 1):
            affiliation = self.graph.nodes[node_id].get('affiliation', 'unknown') if self.graph else 'unknown'
            table.add_row(
                str(i),
                node_id,
                f"{centrality:.4f}",
                affiliation
            )

        console.print(table)

    def export_to_excel(self) -> str:
        """Export all analysis to Excel file."""
        if not self.graph:
            raise ValueError("No graph data to export")

        logger.info("Exporting to Excel...")

        # Create workbook
        workbook = xlwt.Workbook(encoding="utf-8")

        # Export basic statistics
        self._export_statistics_to_excel(workbook)

        # Export organizations
        self._export_organizations_to_excel(workbook)

        # Export centralities
        self._export_centralities_to_excel(workbook)

        # Export nodes list
        self._export_nodes_to_excel(workbook)

        # Export edge analysis
        self._export_edge_analysis_to_excel(workbook)

        # Save file
        base_name = os.path.splitext(os.path.basename(self.config.input_file))[0]
        output_filename = f"{base_name}_report.xls"

        try:
            workbook.save(output_filename)
            logger.info(f"Exported to {output_filename}")
        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")
            raise

        return output_filename

    def _export_statistics_to_excel(self, workbook: xlwt.Workbook) -> None:
        """Export statistics to Excel sheet."""
        sheet = workbook.add_sheet("Graph Statistics")

        sheet.write(0, 0, "Metric")
        sheet.write(0, 1, "Value")

        row = 1
        for key, value in self.stats.items():
            if key == 'isolates':
                continue  # Handled separately
            sheet.write(row, 0, key.replace('_', ' ').title())
            sheet.write(row, 1, str(value))
            row += 1

    def _export_organizations_to_excel(self, workbook: xlwt.Workbook) -> None:
        """Export organization analysis to Excel sheet."""
        sheet = workbook.add_sheet("Top Organizations")

        sheet.write(0, 0, "Organization")
        sheet.write(0, 1, "Node Count")
        sheet.write(0, 2, "Percentage")

        total_nodes = self.stats.get('num_nodes', 0)
        for i, (org, count) in enumerate(self.top_organizations.items(), 1):
            percentage = (count / total_nodes * 100) if total_nodes > 0 else 0
            sheet.write(i, 0, org)
            sheet.write(i, 1, count)
            sheet.write(i, 2, f"{percentage:.2f}%")

    def _export_centralities_to_excel(self, workbook: xlwt.Workbook) -> None:
        """Export centrality analysis to Excel sheet."""
        if not self.centralities:
            return

        sheet = workbook.add_sheet("Centralities")

        sheet.write(0, 0, "Node ID")
        sheet.write(0, 1, "Degree Centrality")
        sheet.write(0, 2, "Affiliation")

        for i, (node_id, centrality) in enumerate(self.centralities, 1):
            affiliation = self.graph.nodes[node_id].get('affiliation', 'unknown') if self.graph else 'unknown'
            sheet.write(i, 0, str(node_id))
            sheet.write(i, 1, centrality)
            sheet.write(i, 2, affiliation)

    def _export_nodes_to_excel(self, workbook: xlwt.Workbook) -> None:
        """Export node list to Excel sheet."""
        if not self.graph:
            return

        sheet = workbook.add_sheet("Nodes")

        sheet.write(0, 0, "Node ID")
        sheet.write(0, 1, "Email")
        sheet.write(0, 2, "Affiliation")

        for i, (node_id, data) in enumerate(self.graph.nodes(data=True), 1):
            sheet.write(i, 0, str(node_id))
            sheet.write(i, 1, data.get('email', ''))
            sheet.write(i, 2, data.get('affiliation', ''))

    def _export_edge_analysis_to_excel(self, workbook: xlwt.Workbook) -> None:
        """Export edge analysis to Excel sheet."""
        edge_analysis = self.calculate_edge_analysis()

        sheet = workbook.add_sheet("Edge Analysis")

        sheet.write(0, 0, "Metric")
        sheet.write(0, 1, "Value")

        sheet.write(1, 0, "Intra-organization edges")
        sheet.write(1, 1, edge_analysis.get('intra_organization_edges', 0))

        sheet.write(2, 0, "Inter-organization edges")
        sheet.write(2, 1, edge_analysis.get('inter_organization_edges', 0))

        # Add organization edge counts
        row = 4
        sheet.write(row, 0, "Organization")
        sheet.write(row, 1, "Edge Count")

        org_edge_counts = edge_analysis.get('organization_edge_counts', {})
        for i, (org, count) in enumerate(org_edge_counts.items(), 1):
            sheet.write(row + i, 0, org)
            sheet.write(row + i, 1, count)


def parse_arguments() -> ReportConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="formatAndReportGraphML",
        description="Comprehensive reporter for GraphML files with organization analysis"
    )

    parser.add_argument(
        "file",
        type=str,
        help="Path to the GraphML network file"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity"
    )

    parser.add_argument(
        "-oi", "--org_list_to_ignore",
        type=lambda s: [item.strip() for item in s.split(',')],
        help="Filter out developers affiliated with organizations in a given list (comma-separated)"
    )

    parser.add_argument(
        "-oo", "--org_list_only",
        type=lambda s: [item.strip() for item in s.split(',')],
        help="Consider only developers affiliated with organizations in a given list (comma-separated)"
    )

    parser.add_argument(
        "-c", "--color_map",
        type=str,
        help="JSON file mapping firms/organizations to colors"
    )

    parser.add_argument(
        "-tn", "--top_n_orgs",
        type=int,
        default=20,
        help="Number of top organizations to report (default: 20)"
    )

    parser.add_argument(
        "-ti", "--top_n_inds",
        type=int,
        default=10,
        help="Number of top individuals to report (default: 10)"
    )

    args = parser.parse_args()

    return ReportConfig(
        input_file=args.file,
        org_list_to_ignore=args.org_list_to_ignore,
        org_list_only=args.org_list_only,
        color_map_file=args.color_map,
        verbose=args.verbose,
        top_n_organizations=args.top_n_orgs,
        top_n_individuals=args.top_n_inds,
    )


def print_banner() -> None:
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   formatAndReportGraphML                     ║
║           Comprehensive GraphML Analysis and Reporting       ║
╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner)


def main() -> None:
    """Main function to orchestrate the GraphML reporting."""
    print_banner()

    try:
        # Parse arguments
        config = parse_arguments()

        # Create reporter
        reporter = GraphMLReporter(config)

        # Load and process graph
        reporter.load_graph()
        reporter.load_color_map()
        reporter.normalize_affiliations()
        reporter.filter_by_organizations()

        # Perform analysis
        reporter.calculate_statistics()
        reporter.calculate_centralities()
        reporter.analyze_organizations()

        # Display results
        reporter.print_statistics()
        reporter.print_organization_analysis()
        reporter.print_centrality_analysis()

        # Export to Excel
        output_file = reporter.export_to_excel()
        console.print(f"\n✅ [bold green]Report saved to:[/bold green] {output_file}")

        logger.success("Analysis completed successfully!")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except nx.NetworkXError as e:
        logger.error(f"NetworkX error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in color map: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()