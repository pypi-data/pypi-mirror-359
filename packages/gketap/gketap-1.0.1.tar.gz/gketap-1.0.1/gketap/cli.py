import click
from rich.console import Console
from .core import (
    discover_clusters,
    start_cluster_tunnel,
    stop_all_tunnels,
    stop_cluster_tunnel,
    show_status,
)

console = Console()

@click.group()
def cli():
    """gketap - Tap into GKE clusters via SSH tunnels through a bastion"""
    pass

@cli.command()
def discover():
    """Discover GKE clusters and generate tunnel config"""
    discover_clusters()

@cli.command()
@click.argument("cluster")
def start(cluster):
    """Start tunnel for a given cluster"""
    start_cluster_tunnel(cluster)

@cli.command()
@click.argument("cluster", required=False)
def stop(cluster):
    """Stop tunnel(s) – either all or one cluster"""
    if cluster:
        stop_cluster_tunnel(cluster)
    else:
        stop_all_tunnels()

@cli.command()
def status():
    """Show tunnel status for all clusters"""
    show_status()
