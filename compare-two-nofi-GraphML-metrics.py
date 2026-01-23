#!/usr/bin/env python3

"""
graphml_metrics_plotter.py - Plot network metrics from multiple GraphML files

This script reads multiple GraphML files, calculates standard network metrics,
and creates plots comparing the metrics across files.

Supported metrics:
- Number of nodes
- Number of edges
- Number of isolates
- Average degree
- Density
- Average clustering coefficient
- Number of connected components
- Size of largest connected component

Usage:
    python graphml_metrics_plotter.py file1.graphml file2.graphml file3.graphml
    python graphml_metrics_plotter.py *.graphml --save-plot metrics_comparison.png
"""

import argparse
import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from utils.unified_logger import logger
from utils.unified_console import console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Plot network metrics from multiple GraphML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s network1.graphml network2.graphml
  %(prog)s *.graphml --save-plot metrics.png
  %(prog)s *.graphml --output-dir results --dpi 150
        """
    )

    parser.add_argument(
        "files",
        type=str,
        nargs='+',
        help="GraphML files to analyze (2-20 files)"
    )

    parser.add_argument(
        "--save-plot",
        type=str,
        default=None,
        help="Save plot to file (e.g., metrics.png, metrics.pdf)"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Output directory for saved plots (default: current directory)"
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=100,
        help="DPI for saved plot (default: 100)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Don't display the plot (only save if --save-plot is specified)"
    )

    parser.add_argument(
        "--no-table",
        action="store_true",
        help="Don't display the Rich table summary"
    )

    return parser.parse_args()


def validate_files(files, verbose=False):
    """Validate input files."""
    if len(files) < 2:
        console.print("[red]✗ Error: At least 2 GraphML files are required for comparison[/red]")
        return False

    if len(files) > 20:
        console.print("[red]✗ Error: Maximum 20 GraphML files are supported[/red]")
        return False

    valid_files = []
    invalid_files = []

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Validating files...", total=len(files))

        for file in files:
            if not os.path.exists(file):
                invalid_files.append((file, "File not found"))
            elif not file.lower().endswith('.graphml'):
                invalid_files.append((file, "Not a .graphml file"))
            else:
                valid_files.append(file)

            progress.update(task, advance=1)

    if invalid_files:
        console.print("\n[bold yellow]⚠ Warning: Invalid files found:[/bold yellow]")
        invalid_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        invalid_table.add_column("File", style="dim", width=40)
        invalid_table.add_column("Reason", style="red")

        for file, reason in invalid_files:
            invalid_table.add_row(file, reason)

        console.print(invalid_table)

    if len(valid_files) < 2:
        console.print("[red]✗ Error: Need at least 2 valid GraphML files[/red]")
        return False

    console.print(f"[green]✓ Found {len(valid_files)} valid GraphML files[/green]")

    return valid_files


def read_graphml_file(filepath):
    """Read and validate a GraphML file."""
    try:
        graph = nx.read_graphml(filepath)
        filename = os.path.basename(filepath)
        return graph, filename, None

    except Exception as e:
        return None, None, str(e)


def calculate_metrics(graph, filename):
    """Calculate various network metrics."""
    metrics = {}

    # Basic metrics
    metrics['filename'] = filename
    metrics['num_nodes'] = graph.number_of_nodes()
    metrics['num_edges'] = graph.number_of_edges()
    metrics['num_isolates'] = nx.number_of_isolates(graph)

    # Degree metrics
    degrees = [d for n, d in graph.degree()]
    metrics['avg_degree'] = np.mean(degrees) if degrees else 0
    metrics['max_degree'] = max(degrees) if degrees else 0
    metrics['min_degree'] = min(degrees) if degrees else 0

    # Graph properties
    metrics['density'] = nx.density(graph) if metrics['num_nodes'] > 1 else 0

    # Clustering coefficient (only for undirected graphs)
    if not nx.is_directed(graph):
        try:
            metrics['avg_clustering'] = nx.average_clustering(graph)
        except:
            metrics['avg_clustering'] = 0
    else:
        metrics['avg_clustering'] = 0

    # Connected components
    if nx.is_directed(graph):
        # Use weakly connected components for directed graphs
        components = list(nx.weakly_connected_components(graph))
    else:
        components = list(nx.connected_components(graph))

    metrics['num_components'] = len(components)

    # Size of largest component
    if components:
        largest_component = max(components, key=len)
        metrics['largest_component_size'] = len(largest_component)
        metrics['largest_component_percentage'] = (len(largest_component) / metrics['num_nodes']) * 100
    else:
        metrics['largest_component_size'] = 0
        metrics['largest_component_percentage'] = 0

    # Graph type
    metrics['is_directed'] = nx.is_directed(graph)
    metrics['is_weighted'] = nx.is_weighted(graph)

    return metrics


def create_metrics_dataframe(all_metrics):
    """Organize metrics into a structured format."""
    data = {
        'filenames': [],
        'num_nodes': [],
        'num_edges': [],
        'num_isolates': [],
        'avg_degree': [],
        'density': [],
        'avg_clustering': [],
        'num_components': [],
        'largest_component_size': [],
        'largest_component_percentage': [],
        'is_directed': [],
        'is_weighted': []
    }

    for metrics in all_metrics:
        data['filenames'].append(metrics['filename'])
        data['num_nodes'].append(metrics['num_nodes'])
        data['num_edges'].append(metrics['num_edges'])
        data['num_isolates'].append(metrics['num_isolates'])
        data['avg_degree'].append(metrics['avg_degree'])
        data['density'].append(metrics['density'])
        data['avg_clustering'].append(metrics['avg_clustering'])
        data['num_components'].append(metrics['num_components'])
        data['largest_component_size'].append(metrics['largest_component_size'])
        data['largest_component_percentage'].append(metrics['largest_component_percentage'])
        data['is_directed'].append(metrics['is_directed'])
        data['is_weighted'].append(metrics['is_weighted'])

    return data


def create_comparison_plot(data, output_dir=".", save_path=None, dpi=100):
    """Create comprehensive comparison plots."""

    filenames = data['filenames']
    n_files = len(filenames)

    # Truncate long filenames for display
    display_names = []
    for name in filenames:
        if len(name) > 20:
            display_names.append(name[:17] + "...")
        else:
            display_names.append(name)

    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Network Metrics Comparison', fontsize=16, fontweight='bold')

    # Plot 1: Basic metrics (Nodes, Edges, Isolates)
    ax1 = plt.subplot(3, 3, 1)
    x = np.arange(n_files)
    width = 0.25

    ax1.bar(x - width, data['num_nodes'], width, label='Nodes', color='skyblue', alpha=0.8)
    ax1.bar(x, data['num_edges'], width, label='Edges', color='lightgreen', alpha=0.8)
    ax1.bar(x + width, data['num_isolates'], width, label='Isolates', color='salmon', alpha=0.8)

    ax1.set_xlabel('Graph Files')
    ax1.set_ylabel('Count')
    ax1.set_title('Basic Network Metrics')
    ax1.set_xticks(x)
    ax1.set_xticklabels(display_names, rotation=45, ha='right', fontsize=9)
    ax1.legend()
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Plot 2: Average Degree
    ax2 = plt.subplot(3, 3, 2)
    bars = ax2.bar(display_names, data['avg_degree'], color='orange', alpha=0.7)
    ax2.set_xlabel('Graph Files')
    ax2.set_ylabel('Average Degree')
    ax2.set_title('Average Node Degree')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3, linestyle='--')

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height + 0.05,
                 f'{height:.2f}', ha='center', va='bottom', fontsize=8)

    # Plot 3: Density
    ax3 = plt.subplot(3, 3, 3)
    bars = ax3.bar(display_names, data['density'], color='purple', alpha=0.7)
    ax3.set_xlabel('Graph Files')
    ax3.set_ylabel('Density')
    ax3.set_title('Network Density')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3, linestyle='--')

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2., height + 0.0005,
                 f'{height:.4f}', ha='center', va='bottom', fontsize=8)

    # Plot 4: Clustering Coefficient
    ax4 = plt.subplot(3, 3, 4)
    bars = ax4.bar(display_names, data['avg_clustering'], color='red', alpha=0.7)
    ax4.set_xlabel('Graph Files')
    ax4.set_ylabel('Clustering Coefficient')
    ax4.set_title('Average Clustering Coefficient')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3, linestyle='--')

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width() / 2., height + 0.005,
                 f'{height:.3f}', ha='center', va='bottom', fontsize=8)

    # Plot 5: Number of Components
    ax5 = plt.subplot(3, 3, 5)
    bars = ax5.bar(display_names, data['num_components'], color='green', alpha=0.7)
    ax5.set_xlabel('Graph Files')
    ax5.set_ylabel('Number of Components')
    ax5.set_title('Connected Components')
    ax5.tick_params(axis='x', rotation=45)
    ax5.grid(True, alpha=0.3, linestyle='--')

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width() / 2., height + 0.05,
                 f'{int(height)}', ha='center', va='bottom', fontsize=8)

    # Plot 6: Largest Component Percentage
    ax6 = plt.subplot(3, 3, 6)
    bars = ax6.bar(display_names, data['largest_component_percentage'], color='brown', alpha=0.7)
    ax6.set_xlabel('Graph Files')
    ax6.set_ylabel('Percentage (%)')
    ax6.set_title('Largest Component (% of nodes)')
    ax6.tick_params(axis='x', rotation=45)
    ax6.grid(True, alpha=0.3, linestyle='--')

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                 f'{height:.1f}%', ha='center', va='bottom', fontsize=8)

    # Plot 7: Scatter plot - Nodes vs Edges
    ax7 = plt.subplot(3, 3, 7)
    scatter = ax7.scatter(data['num_nodes'], data['num_edges'],
                          c=np.arange(n_files), cmap='viridis', s=100, alpha=0.7)
    ax7.set_xlabel('Number of Nodes')
    ax7.set_ylabel('Number of Edges')
    ax7.set_title('Nodes vs Edges')
    ax7.grid(True, alpha=0.3, linestyle='--')

    # Add labels to scatter points
    for i, (x, y) in enumerate(zip(data['num_nodes'], data['num_edges'])):
        ax7.text(x, y, f' {i + 1}', fontsize=9, va='center')

    # Plot 8: Directed/Weighted indicators
    ax8 = plt.subplot(3, 3, 8)

    # Prepare data for stacked bar chart
    directed_count = sum(data['is_directed'])
    undirected_count = n_files - directed_count
    weighted_count = sum(data['is_weighted'])
    unweighted_count = n_files - weighted_count

    categories = ['Directed', 'Undirected', 'Weighted', 'Unweighted']
    counts = [directed_count, undirected_count, weighted_count, unweighted_count]
    colors = ['blue', 'lightblue', 'orange', 'lightyellow']

    bars = ax8.bar(categories, counts, color=colors, alpha=0.7)
    ax8.set_ylabel('Count')
    ax8.set_title('Graph Types')
    ax8.grid(True, alpha=0.3, linestyle='--')

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax8.text(bar.get_x() + bar.get_width() / 2., height + 0.05,
                 f'{int(height)}', ha='center', va='bottom')

    # Plot 9: Summary statistics table
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('tight')
    ax9.axis('off')

    # Create summary table
    summary_data = []
    for i, filename in enumerate(display_names):
        summary_data.append([
            f"{i + 1}",
            filename,
            f"{data['num_nodes'][i]:,}",
            f"{data['num_edges'][i]:,}",
            f"{data['num_isolates'][i]}"
        ])

    table = ax9.table(
        cellText=summary_data,
        colLabels=['#', 'File', 'Nodes', 'Edges', 'Isolates'],
        cellLoc='center',
        loc='center',
        colWidths=[0.05, 0.25, 0.15, 0.15, 0.15]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)
    ax9.set_title('Summary Table')

    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.95, hspace=0.4, wspace=0.3)

    # Save plot if requested
    if save_path:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Construct full save path
        if output_dir != ".":
            full_save_path = os.path.join(output_dir, save_path)
        else:
            full_save_path = save_path

        plt.savefig(full_save_path, dpi=dpi, bbox_inches='tight')
        console.print(f"[green]✓ Plot saved to: [bold]{full_save_path}[/bold][/green]")

    return fig


def create_rich_metrics_table(data):
    """Create a Rich table with metrics summary."""

    # Create main table
    table = Table(
        title="[bold cyan]Network Metrics Summary[/bold cyan]",
        box=box.ROUNDED,
        header_style="bold magenta",
        title_style="bold cyan",
        caption=f"Total files: {len(data['filenames'])}",
        show_lines=True,
    )

    # Add columns
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Filename", style="cyan", width=25)
    table.add_column("Nodes", justify="right", style="green")
    table.add_column("Edges", justify="right", style="green")
    table.add_column("Isolates", justify="right", style="yellow")
    table.add_column("Avg Deg", justify="right", style="blue")
    table.add_column("Density", justify="right", style="magenta")
    table.add_column("Clustering", justify="right", style="red")
    table.add_column("Components", justify="right", style="green")
    table.add_column("Largest %", justify="right", style="cyan")
    table.add_column("Dir", justify="center", style="yellow")
    table.add_column("Wgt", justify="center", style="yellow")

    # Add rows
    for i in range(len(data['filenames'])):
        # Color code based on values
        node_color = "green" if data['num_nodes'][i] > np.median(data['num_nodes']) else "dim"
        edge_color = "green" if data['num_edges'][i] > np.median(data['num_edges']) else "dim"
        isolate_color = "red" if data['num_isolates'][i] > np.median(data['num_isolates']) else "dim"

        table.add_row(
            str(i + 1),
            data['filenames'][i][:25],
            f"[{node_color}]{data['num_nodes'][i]:,}[/{node_color}]",
            f"[{edge_color}]{data['num_edges'][i]:,}[/{edge_color}]",
            f"[{isolate_color}]{data['num_isolates'][i]:,}[/{isolate_color}]",
            f"{data['avg_degree'][i]:.2f}",
            f"{data['density'][i]:.4f}",
            f"{data['avg_clustering'][i]:.3f}",
            f"{data['num_components'][i]:,}",
            f"{data['largest_component_percentage'][i]:.1f}%",
            "✓" if data['is_directed'][i] else "✗",
            "✓" if data['is_weighted'][i] else "✗"
        )

    # Add summary row
    table.add_row(
        "[bold]AVG[/bold]",
        "",
        f"[bold]{np.mean(data['num_nodes']):.0f}[/bold]",
        f"[bold]{np.mean(data['num_edges']):.0f}[/bold]",
        f"[bold]{np.mean(data['num_isolates']):.0f}[/bold]",
        f"[bold]{np.mean(data['avg_degree']):.2f}[/bold]",
        f"[bold]{np.mean(data['density']):.4f}[/bold]",
        f"[bold]{np.mean(data['avg_clustering']):.3f}[/bold]",
        f"[bold]{np.mean(data['num_components']):.0f}[/bold]",
        f"[bold]{np.mean(data['largest_component_percentage']):.1f}%[/bold]",
        f"[bold]{sum(data['is_directed'])}/{len(data['filenames'])}[/bold]",
        f"[bold]{sum(data['is_weighted'])}/{len(data['filenames'])}[/bold]",
        style="bold"
    )

    return table


def create_statistics_panel(data):
    """Create a Rich panel with statistics summary."""

    # Calculate statistics
    stats_text = Text()
    stats_text.append("\n")
    stats_text.append("📊 ", style="bold cyan")
    stats_text.append("Overall Statistics:\n", style="bold")

    # Nodes stats
    stats_text.append("  • Nodes: ", style="bold")
    stats_text.append(f"Min={min(data['num_nodes']):,}, ", style="dim")
    stats_text.append(f"Max={max(data['num_nodes']):,}, ", style="dim")
    stats_text.append(f"Avg={np.mean(data['num_nodes']):.0f}\n", style="green")

    # Edges stats
    stats_text.append("  • Edges: ", style="bold")
    stats_text.append(f"Min={min(data['num_edges']):,}, ", style="dim")
    stats_text.append(f"Max={max(data['num_edges']):,}, ", style="dim")
    stats_text.append(f"Avg={np.mean(data['num_edges']):.0f}\n", style="green")

    # Network properties
    stats_text.append("  • Density Range: ", style="bold")
    stats_text.append(f"{min(data['density']):.4f} - {max(data['density']):.4f}\n", style="magenta")

    # Graph types
    directed_pct = (sum(data['is_directed']) / len(data['filenames'])) * 100
    weighted_pct = (sum(data['is_weighted']) / len(data['filenames'])) * 100

    stats_text.append("  • Graph Types: ", style="bold")
    stats_text.append(f"{directed_pct:.1f}% directed, ", style="yellow")
    stats_text.append(f"{weighted_pct:.1f}% weighted\n", style="yellow")

    return Panel(
        stats_text,
        title="[bold]Statistics[/bold]",
        border_style="cyan",
        padding=(1, 2)
    )


def main():
    """Main function."""

    # ASCII art header
    header = """
    ╔═══════════════════════════════════════════════════════╗
    ║      GraphML Metrics Plotter & Analyzer              ║
    ║         Network Analysis Visualization Tool          ║
    ╚═══════════════════════════════════════════════════════╝
    """

    console.print(Panel.fit(header, border_style="cyan"))

    # Parse arguments
    args = parse_arguments()

    # Validate files
    console.print("\n[bold cyan]🔍 File Validation:[/bold cyan]")
    valid_files = validate_files(args.files, args.verbose)
    if not valid_files:
        logger.error("Invalid input files. Exiting.")
        sys.exit(1)

    # Process files with progress bar
    console.print("\n[bold cyan]📂 Processing GraphML Files:[/bold cyan]")

    all_metrics = []
    failed_files = []

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[cyan]{task.fields[filename]}"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
    ) as progress:

        task = progress.add_task(
            "[cyan]Analyzing networks...",
            total=len(valid_files),
            filename=""
        )

        for filepath in valid_files:
            filename = os.path.basename(filepath)
            progress.update(task, filename=filename[:20] + "..." if len(filename) > 20 else filename)

            graph, filename, error = read_graphml_file(filepath)

            if graph is not None:
                metrics = calculate_metrics(graph, filename)
                all_metrics.append(metrics)
            else:
                failed_files.append((filepath, error))

            progress.update(task, advance=1)

    if len(all_metrics) < 2:
        console.print("[red]✗ Error: Need at least 2 successfully processed files for comparison[/red]")
        sys.exit(1)

    # Organize data
    data = create_metrics_dataframe(all_metrics)

    # Display Rich table
    if not args.no_table:
        console.print("\n")
        table = create_rich_metrics_table(data)
        console.print(table)

        # Display statistics panel
        stats_panel = create_statistics_panel(data)
        console.print(stats_panel)

    # Show failed files
    if failed_files:
        console.print("\n[bold yellow]⚠ Warning: Failed to process some files:[/bold yellow]")
        failed_table = Table(show_header=True, header_style="bold red", box=box.SIMPLE)
        failed_table.add_column("File", style="dim", width=40)
        failed_table.add_column("Error", style="red")

        for file, error in failed_files:
            failed_table.add_row(file, error)

        console.print(failed_table)

    # Create and display plot
    console.print("\n[bold cyan]🎨 Creating Visualization:[/bold cyan]")

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Generating plots...", total=100)

        # Simulate progress for plot creation
        for i in range(10):
            progress.update(task, advance=10)
            import time
            time.sleep(0.1)

    fig = create_comparison_plot(
        data,
        output_dir=args.output_dir,
        save_path=args.save_plot,
        dpi=args.dpi
    )

    # Show plot by default (unless --no-show is specified)
    if not args.no_show:
        console.print("\n[bold cyan]📊 Displaying Plot:[/bold cyan]")
        console.print("[dim]Close the plot window to continue...[/dim]")
        plt.show()
    else:
        plt.close(fig)

    # Final summary
    console.print("\n" + "═" * 60)

    summary_panel = Panel.fit(
        f"""
[bold]✅ Analysis Complete![/bold]

📁 [cyan]Processed:[/cyan] [green]{len(all_metrics)}[/green] files
❌ [cyan]Failed:[/cyan] [red]{len(failed_files)}[/red] files
🎨 [cyan]Plot:[/cyan] {'Saved' if args.save_plot else 'Displayed'}

[dim]Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]
        """,
        title="[bold green]Summary[/bold green]",
        border_style="green",
        padding=(1, 2)
    )

    console.print(summary_panel)
    console.print("═" * 60)


if __name__ == "__main__":
    # Import time for timestamp
    import time

    main()