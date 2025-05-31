#!/usr/bin/env python3
"""
Copilot Code Analysis Tool - Main Entry Point
Tracks and analyzes Copilot vs human-written code in repositories.
"""

import click
import json
import os
import sys
import threading
import time
from pathlib import Path

from analyzer.code_analyzer import CodeAnalyzer
from monitoring.file_watcher import FileWatcher
from api.external_client import ExternalAPIClient
from storage.data_manager import DataManager
from dashboard.server import DashboardServer
from utils.logger import setup_logger
from utils.helpers import load_config, validate_config

logger = setup_logger(__name__)

@click.group()
@click.option('--config', default='config.json', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Copilot Code Analysis Tool - Track AI vs Human written code"""
    ctx.ensure_object(dict)
    
    if not os.path.exists(config):
        click.echo(f"Configuration file '{config}' not found. Creating default config...")
        create_default_config(config)
    
    try:
        ctx.obj['config'] = load_config(config)
        validate_config(ctx.obj['config'])
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--repository', '-r', required=True, help='Path to repository to analyze')
@click.option('--output', '-o', help='Output file for analysis results')
@click.pass_context
def analyze(ctx, repository, output):
    """Analyze a repository for Copilot vs human-written code"""
    if not os.path.exists(repository):
        click.echo(f"Repository path '{repository}' does not exist", err=True)
        return
    
    config = ctx.obj['config']
    analyzer = CodeAnalyzer(config)
    data_manager = DataManager(config['storage']['data_file'])
    
    click.echo(f"Analyzing repository: {repository}")
    
    try:
        results = analyzer.analyze_repository(repository)
        
        # Store results
        data_manager.store_analysis_result(repository, results)
        
        # Display summary
        display_analysis_summary(results)
        
        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"Results saved to: {output}")
        
        # Send to external API if configured
        if config.get('api', {}).get('enabled', False):
            api_client = ExternalAPIClient(config['api'])
            try:
                api_client.send_metrics(results)
                click.echo("Metrics sent to external API successfully")
            except Exception as e:
                logger.error(f"Failed to send metrics to external API: {e}")
                click.echo(f"Warning: Failed to send metrics to external API: {e}")
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        click.echo(f"Analysis failed: {e}", err=True)

@cli.command()
@click.option('--repository', '-r', required=True, help='Path to repository to monitor')
@click.option('--interval', '-i', default=300, help='Sync interval in seconds (default: 300)')
@click.pass_context
def monitor(ctx, repository, interval):
    """Monitor a repository for changes and track metrics continuously"""
    if not os.path.exists(repository):
        click.echo(f"Repository path '{repository}' does not exist", err=True)
        return
    
    config = ctx.obj['config']
    analyzer = CodeAnalyzer(config)
    data_manager = DataManager(config['storage']['data_file'])
    watcher = FileWatcher(repository, analyzer, data_manager)
    
    # Setup external API client if enabled
    api_client = None
    if config.get('api', {}).get('enabled', False):
        api_client = ExternalAPIClient(config['api'])
    
    click.echo(f"Starting monitoring of repository: {repository}")
    click.echo(f"Sync interval: {interval} seconds")
    click.echo("Press Ctrl+C to stop monitoring")
    
    try:
        # Start file watcher
        watcher.start()
        
        # Periodic sync to external API
        def sync_metrics():
            while True:
                try:
                    time.sleep(interval)
                    if api_client:
                        latest_results = data_manager.get_latest_results(repository)
                        if latest_results:
                            api_client.send_metrics(latest_results)
                            logger.info("Metrics synced to external API")
                except Exception as e:
                    logger.error(f"Sync error: {e}")
        
        if api_client:
            sync_thread = threading.Thread(target=sync_metrics, daemon=True)
            sync_thread.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        click.echo("\nStopping monitoring...")
        watcher.stop()

@cli.command()
@click.option('--port', '-p', default=5000, help='Dashboard port (default: 5000)')
@click.pass_context
def dashboard(ctx, port):
    """Start the local dashboard web server"""
    config = ctx.obj['config']
    data_manager = DataManager(config['storage']['data_file'])
    
    dashboard_server = DashboardServer(data_manager, config)
    
    click.echo(f"Starting dashboard server on http://0.0.0.0:{port}")
    click.echo("Press Ctrl+C to stop the server")
    
    try:
        dashboard_server.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        click.echo("\nShutting down dashboard server...")

@cli.command()
@click.pass_context
def status(ctx):
    """Show current status and recent metrics"""
    config = ctx.obj['config']
    data_manager = DataManager(config['storage']['data_file'])
    
    repositories = data_manager.get_monitored_repositories()
    
    if not repositories:
        click.echo("No repositories being monitored")
        return
    
    click.echo("Monitored Repositories:")
    click.echo("=" * 50)
    
    for repo in repositories:
        latest = data_manager.get_latest_results(repo)
        if latest:
            click.echo(f"\nRepository: {repo}")
            click.echo(f"Last Analysis: {latest.get('timestamp', 'Unknown')}")
            display_analysis_summary(latest)

def create_default_config(config_path):
    """Create a default configuration file"""
    default_config = {
        "analysis": {
            "supported_extensions": [".py", ".js", ".java", ".cpp", ".c", ".go", ".rs", ".ts"],
            "ignore_patterns": ["*.min.js", "node_modules/*", "__pycache__/*", ".git/*"],
            "copilot_indicators": {
                "comment_patterns": [
                    "# Copilot suggestion",
                    "// Copilot suggestion",
                    "# Generated by GitHub Copilot",
                    "// Generated by GitHub Copilot"
                ],
                "high_velocity_threshold": 100,
                "perfect_syntax_weight": 0.3,
                "common_patterns_weight": 0.4
            }
        },
        "storage": {
            "data_file": "analysis_data.db"
        },
        "api": {
            "enabled": False,
            "endpoint": "",
            "api_key": "",
            "timeout": 30
        },
        "monitoring": {
            "file_patterns": ["*.py", "*.js", "*.java", "*.cpp", "*.c", "*.go", "*.rs", "*.ts"],
            "debounce_delay": 2
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    click.echo(f"Default configuration created at '{config_path}'")
    click.echo("Please edit the configuration file to match your requirements")

def display_analysis_summary(results):
    """Display a formatted summary of analysis results"""
    summary = results.get('summary', {})
    
    click.echo(f"Total Files: {summary.get('total_files', 0)}")
    click.echo(f"Total Lines: {summary.get('total_lines', 0)}")
    click.echo(f"Copilot Lines: {summary.get('copilot_lines', 0)} ({summary.get('copilot_percentage', 0):.1f}%)")
    click.echo(f"Human Lines: {summary.get('human_lines', 0)} ({summary.get('human_percentage', 0):.1f}%)")
    
    if 'language_breakdown' in results:
        click.echo("\nLanguage Breakdown:")
        for lang, stats in results['language_breakdown'].items():
            click.echo(f"  {lang}: {stats.get('copilot_percentage', 0):.1f}% Copilot")

if __name__ == '__main__':
    cli()
