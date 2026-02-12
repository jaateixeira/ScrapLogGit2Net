#!/usr/bin/env python3
"""
formatAndReportGraphML - Basic reporter for GraphML files with company analysis.
"""

import argparse
import os
import sys
import json
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass

import networkx as nx
import xlwt
from rich.panel import Panel

from utils.unified_logger import logger
from utils.unified_console import console, traceback
from utils.unified_console import Table



@dataclass
class ReportConfig:
    """Configuration for basic GraphML reporting."""
    input_file: str
    color_map_file: Optional[str] = None
    top_firms_only: bool = False
    filter_by_org: bool = False
    verbose: bool = False
    output_prefix: Optional[str] = None

    # Default company lists
    top_firms_that_matter: List[str] = None
    top_firms_that_do_not_matter: List[str] = None

    def __post_init__(self):
        """Initialize default company lists if not provided."""
        if self.top_firms_that_matter is None:
            self.top_firms_that_matter = [
                'google', 'microsoft', 'ibm', 'amazon', 'intel',
                'amd', 'nvidia', 'arm', 'meta', 'bytedance'
            ]

        if self.top_firms_that_do_not_matter is None:
            self.top_firms_that_do_not_matter = ['users', 'tensorflow', 'gmail']

        if self.output_prefix is None and self.input_file:
            self.output_prefix = os.path.splitext(os.path.basename(self.input_file))[0]


class BasicGraphMLReporter:
    """Handles basic GraphML file analysis and reporting."""

    def __init__(self, config: ReportConfig):
        self.config = config
        self.graph: Optional[nx.Graph] = None
        self.color_map: Dict[str, str] = {}
        self.degree_centrality: Dict[str, float] = {}
        self.top_connected_individuals: List[Tuple[str, float]] = []
        self.organization_counts: Dict[str, int] = {}

    def load_graph(self) -> None:
        """Load GraphML file with error handling."""
        console.print(f"[bold cyan]Loading GraphML file:[/bold cyan] {self.config.input_file}")

        try:
            self.graph = nx.read_graphml(self.config.input_file)
            console.print(f"[green]✓ Graph imported successfully[/green]")
        except Exception as e:
            logger.error(f"Failed to load GraphML file: {e}")
            raise

        self._print_basic_stats()

    def _print_basic_stats(self) -> None:
        """Print basic graph statistics."""
        if not self.graph:
            return

        stats_panel = Panel.fit(
            f"[bold]Nodes:[/bold] {self.graph.number_of_nodes()}\n"
            f"[bold]Edges:[/bold] {self.graph.number_of_edges()}\n"
            f"[bold]Isolates:[/bold] {nx.number_of_isolates(self.graph)}",
            title="Graph Statistics",
            border_style="blue"
        )
        console.print(stats_panel)

    def load_color_map(self) -> None:
        """Load color map from JSON file if provided."""
        if not self.config.color_map_file:
            return

        try:
            with open(self.config.color_map_file, 'r') as file:
                self.color_map = json.load(file)
            console.print(f"[green]✓ Loaded color map from {self.config.color_map_file}[/green]")
        except FileNotFoundError:
            logger.warning(f"Color map file not found: {self.config.color_map_file}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in color map file: {self.config.color_map_file}")

    def normalize_affiliations(self) -> None:
        """Normalize affiliation domains."""
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

    def filter_graph(self) -> None:
        """Filter graph based on configuration options."""
        if not self.graph:
            return

        original_node_count = self.graph.number_of_nodes()

        # Filter out unwanted organizations
        if self.config.filter_by_org:
            self._filter_by_organizations(
                self.config.top_firms_that_do_not_matter,
                keep=False
            )

        # Keep only top firms
        if self.config.top_firms_only:
            self._filter_by_organizations(
                self.config.top_firms_that_matter,
                keep=True
            )

        filtered_count = original_node_count - self.graph.number_of_nodes()
        if filtered_count > 0:
            console.print(f"[yellow]Filtered out {filtered_count} nodes[/yellow]")

    def _filter_by_organizations(self, org_list: List[str], keep: bool = True) -> None:
        """Internal method to filter nodes by organization."""
        if not self.graph:
            return

        operation = "Keeping only" if keep else "Removing"
        console.print(f"[cyan]{operation} organizations: {org_list}[/cyan]")

        nodes_to_remove = []
        for node, data in self.graph.nodes(data=True):
            affiliation = data.get('affiliation', '')
            should_remove = (affiliation not in org_list) if keep else (affiliation in org_list)

            if should_remove:
                nodes_to_remove.append(node)
                if self.config.verbose:
                    action = "Removing" if not keep else "Filtering out"
                    console.print(f"  {action} node {node} ({affiliation})")

        self.graph.remove_nodes_from(nodes_to_remove)

    def analyze_centralities(self) -> None:
        """Calculate and analyze centrality measures."""
        if not self.graph:
            return

        console.print("[bold cyan]Calculating centralities...[/bold cyan]")

        try:
            self.degree_centrality = nx.degree_centrality(self.graph)
            self.top_connected_individuals = sorted(
                self.degree_centrality.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 connected individuals
        except Exception as e:
            logger.error(f"Error calculating centralities: {e}")
            self.degree_centrality = {}
            self.top_connected_individuals = []

    def analyze_organizations(self) -> None:
        """Analyze organizations by node count."""
        if not self.graph:
            return

        console.print("[bold cyan]Analyzing organizations...[/bold cyan]")

        self.organization_counts = {}
        for _, data in self.graph.nodes(data=True):
            affiliation = data.get('affiliation', 'unknown')
            self.organization_counts[affiliation] = self.organization_counts.get(affiliation, 0) + 1

        # Sort by count descending
        self.organization_counts = dict(
            sorted(
                self.organization_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )

    def print_analysis_summary(self) -> None:
        """Print comprehensive analysis summary."""
        if not self.graph:
            return

        # Print isolates if any
        isolates = list(nx.isolates(self.graph))
        if isolates:
            console.print("\n[bold yellow]Isolated Nodes:[/bold yellow]")
            for isolate in isolates[:5]:  # Show first 5 only
                data = self.graph.nodes[isolate]
                console.print(f"  • {isolate}: {data.get('e-mail', 'N/A')} @ {data.get('affiliation', 'N/A')}")
            if len(isolates) > 5:
                console.print(f"  ... and {len(isolates) - 5} more")

        # Print top connected individuals
        if self.top_connected_individuals:
            console.print("\n[bold cyan]Top 10 Most Connected Individuals:[/bold cyan]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Rank", style="dim")
            table.add_column("Email", style="green")
            table.add_column("Centrality", style="yellow")
            table.add_column("Affiliation", style="cyan")

            for i, (node_id, centrality) in enumerate(self.top_connected_individuals, 1):
                data = self.graph.nodes[node_id]
                email = data.get('e-mail', 'N/A')
                affiliation = data.get('affiliation', 'unknown')
                table.add_row(
                    str(i),
                    email,
                    f"{centrality:.4f}",
                    affiliation
                )

            console.print(table)

        # Print top organizations
        if self.organization_counts:
            top_n = 10
            top_orgs = list(self.organization_counts.items())[:top_n]

            console.print(f"\n[bold cyan]Top {len(top_orgs)} Organizations by Node Count:[/bold cyan]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Rank", style="dim")
            table.add_column("Organization", style="green")
            table.add_column("Node Count", style="yellow")
            table.add_column("Percentage", style="cyan")

            total_nodes = self.graph.number_of_nodes()
            for i, (org, count) in enumerate(top_orgs, 1):
                percentage = (count / total_nodes * 100) if total_nodes > 0 else 0
                table.add_row(
                    str(i),
                    org,
                    str(count),
                    f"{percentage:.1f}%"
                )

            console.print(table)

            # Show all affiliations if verbose
            if self.config.verbose and len(self.organization_counts) > top_n:
                console.print(f"\n[yellow]All {len(self.organization_counts)} organizations:[/yellow]")
                for org, count in list(self.organization_counts.items())[top_n:top_n + 20]:
                    console.print(f"  {org}: {count}")
                if len(self.organization_counts) > top_n + 20:
                    console.print(f"  ... and {len(self.organization_counts) - (top_n + 20)} more")

    def export_to_excel(self) -> str:
        """Export analysis to Excel file."""
        if not self.graph:
            raise ValueError("No graph data to export")

        console.print("[bold cyan]Exporting to Excel...[/bold cyan]")

        # Create workbook
        workbook = xlwt.Workbook(encoding="utf-8")

        # Export basic statistics
        self._export_basic_stats(workbook)

        # Export organization analysis
        self._export_organization_analysis(workbook)

        # Export node list
        self._export_node_list(workbook)

        # Export centrality analysis
        self._export_centrality_analysis(workbook)

        # Save file
        output_filename = f"{self.config.output_prefix}.xls"

        try:
            workbook.save(output_filename)
            console.print(f"[green]✓ Report saved to: {output_filename}[/green]")
        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")
            raise

        return output_filename

    def _export_basic_stats(self, workbook: xlwt.Workbook) -> None:
        """Export basic statistics to Excel."""
        sheet = workbook.add_sheet("Graph Statistics")

        sheet.write(0, 0, "Metric")
        sheet.write(0, 1, "Value")

        stats = [
            ("Number of nodes", self.graph.number_of_nodes()),
            ("Number of edges", self.graph.number_of_edges()),
            ("Number of isolates", nx.number_of_isolates(self.graph)),
        ]

        for i, (metric, value) in enumerate(stats, 1):
            sheet.write(i, 0, metric)
            sheet.write(i, 1, value)

    def _export_organization_analysis(self, workbook: xlwt.Workbook) -> None:
        """Export organization analysis to Excel."""
        sheet = workbook.add_sheet("Organizations by Node Count")

        sheet.write(0, 0, "Organization")
        sheet.write(0, 1, "Node Count")
        sheet.write(0, 2, "Percentage")

        total_nodes = self.graph.number_of_nodes()
        for i, (org, count) in enumerate(self.organization_counts.items(), 1):
            percentage = (count / total_nodes * 100) if total_nodes > 0 else 0
            sheet.write(i, 0, org)
            sheet.write(i, 1, count)
            sheet.write(i, 2, f"{percentage:.2f}%")

    def _export_node_list(self, workbook: xlwt.Workbook) -> None:
        """Export node list to Excel."""
        sheet = workbook.add_sheet("Nodes (Developers)")

        sheet.write(0, 0, "ID")
        sheet.write(0, 1, "Email")
        sheet.write(0, 2, "Affiliation")

        # Try to write nodes in order if they're numeric
        try:
            nodes_sorted = sorted(self.graph.nodes(), key=lambda x: int(x))
        except (ValueError, TypeError):
            nodes_sorted = list(self.graph.nodes())

        for i, node in enumerate(nodes_sorted, 1):
            data = self.graph.nodes[node]
            sheet.write(i, 0, str(node))
            sheet.write(i, 1, data.get('e-mail', ''))
            sheet.write(i, 2, data.get('affiliation', ''))

    def _export_centrality_analysis(self, workbook: xlwt.Workbook) -> None:
        """Export centrality analysis to Excel."""
        if not self.degree_centrality:
            return

        sheet = workbook.add_sheet("Centrality Analysis")

        sheet.write(0, 0, "Node ID")
        sheet.write(0, 1, "Degree Centrality")
        sheet.write(0, 2, "Email")
        sheet.write(0, 3, "Affiliation")

        # Sort by centrality descending
        sorted_centralities = sorted(
            self.degree_centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for i, (node_id, centrality) in enumerate(sorted_centralities, 1):
            data = self.graph.nodes[node_id]
            sheet.write(i, 0, str(node_id))
            sheet.write(i, 1, centrality)
            sheet.write(i, 2, data.get('e-mail', ''))
            sheet.write(i, 3, data.get('affiliation', ''))


def parse_arguments() -> ReportConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="formatAndReportGraphML",
        description="Basic reporter for GraphML files with company analysis"
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
        "-t", "--top-firms-only",
        action="store_true",
        help=f"Only include top tech firms (Google, Microsoft, IBM, etc.)"
    )

    parser.add_argument(
        "-f", "--filter-by-org",
        action="store_true",
        help=f"Filter out generic organizations (users, tensorflow, gmail)"
    )

    parser.add_argument(
        "-c", "--color-map",
        type=str,
        dest="color_map_file",
        help="JSON file mapping firms/organizations to colors"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        dest="output_prefix",
        help="Output filename prefix (default: input filename without extension)"
    )

    parser.add_argument(
        "--top-firms",
        type=lambda s: [item.strip() for item in s.split(',')],
        help="Comma-separated list of top firms to consider (overrides default)"
    )

    parser.add_argument(
        "--filter-firms",
        type=lambda s: [item.strip() for item in s.split(',')],
        help="Comma-separated list of firms to filter out (overrides default)"
    )

    args = parser.parse_args()

    return ReportConfig(
        input_file=args.file,
        color_map_file=args.color_map_file,
        top_firms_only=args.top_firms_only,
        filter_by_org=args.filter_by_org,
        verbose=args.verbose,
        output_prefix=args.output_prefix,
        top_firms_that_matter=args.top_firms,
        top_firms_that_do_not_matter=args.filter_firms,
    )


def print_banner() -> None:
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   formatAndReportGraphML                     ║
║          Basic GraphML Analysis and Reporting Tool           ║
║       Visualizing company networks since June 2024           ║
╚══════════════════════════════════════════════════════════════╝

    [dim]TODO:[/dim]
    [dim]• Report on companies with more developers[/dim]
    [dim]• Report on centrality of developers and organizations[/dim]
    [dim]• Export in XML, HTML, LaTeX, MD, CSV and TXT files[/dim]
    """
    console.print(banner)


def main() -> None:
    """Main function to orchestrate the GraphML reporting."""
    print_banner()

    try:
        # Parse arguments
        config = parse_arguments()


        # Display configuration
        if config.verbose:
            config_table = Table(title="Configuration", show_header=False, box=None)
            config_table.add_column("Key", style="cyan")
            config_table.add_column("Value", style="green")

            config_table.add_row("Input file", config.input_file)
            config_table.add_row("Top firms only", str(config.top_firms_only))
            config_table.add_row("Filter by org", str(config.filter_by_org))
            config_table.add_row("Color map", config.color_map_file or "None")
            config_table.add_row("Output prefix", config.output_prefix)

            console.print(config_table)

        # Create reporter
        reporter = BasicGraphMLReporter(config)

        # Load and process graph
        reporter.load_graph()
        reporter.load_color_map()
        reporter.normalize_affiliations()
        reporter.filter_graph()

        # Perform analysis
        reporter.analyze_centralities()
        reporter.analyze_organizations()

        # Display results
        reporter.print_analysis_summary()

        # Export to Excel
        output_file = reporter.export_to_excel()

        console.print(f"\n✅ [bold green]Analysis completed![/bold green]")
        console.print(f"   Report saved as: [cyan]{output_file}[/cyan]")

    except FileNotFoundError as e:
        console.print(f"\n❌ [bold red]Error: File not found[/bold red]")
        console.print(f"   {e}")
        sys.exit(1)
    except nx.NetworkXError as e:
        console.print(f"\n❌ [bold red]NetworkX Error:[/bold red]")
        console.print(f"   {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"\n❌ [bold red]JSON Error: Invalid color map file[/bold red]")
        console.print(f"   {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ [bold red]Unexpected error:[/bold red]")
        console.print(f"   {e}")
        console.print(traceback)
        sys.exit(1)


if __name__ == "__main__":
    main()