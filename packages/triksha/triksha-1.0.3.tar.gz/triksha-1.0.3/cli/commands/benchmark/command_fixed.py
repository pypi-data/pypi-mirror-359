"""Main benchmark command implementation"""
from rich.console import Console
from rich.panel import Panel
from typing import Optional, Dict, Any, List, Tuple, Union, Set, Callable
import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import time
import inquirer
import traceback
import uuid
import asyncio
import random
import subprocess
import glob
import logging
import numpy as np
import shutil
import pytz
import asyncio
import json
import re
import csv
import time
import subprocess
import ast
import hashlib
import uuid
import traceback
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.live import Live
from rich.layout import Layout
from rich.columns import Columns
import importlib.util
import pkg_resources
import re

from .runners import APIBenchmarkRunner, KubernetesBenchmarkManager
from .results import ResultsViewer
from .ui import BenchmarkUI
from benchmarks.utils.backup_manager import BackupManager
from system_monitor import setup_system_monitor
from cli.notification.email_service import EmailNotificationService

# Add retry-related imports
import random
from enum import Enum


class RetryableError(Exception):
    """Exception for errors that should be retried"""
    pass


class RateLimitError(RetryableError):
    """Exception for rate limit errors"""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class RetryConfig:
    """Configuration for retry logic"""
    def __init__(self, 
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int, suggested_delay: Optional[float] = None) -> float:
        """Calculate delay for the given attempt number"""
        if suggested_delay:
            # If the API suggests a specific delay (e.g., Retry-After header), use it
            delay = min(suggested_delay, self.max_delay)
        else:
            # Calculate exponential backoff delay
            delay = self.base_delay * (self.exponential_base ** attempt)
            delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable"""
    error_str = str(error).lower()
    
    # Rate limit errors
    rate_limit_indicators = [
        'rate limit', 'rate_limit', 'ratelimit',
        'too many requests', 'quota exceeded',
        'throttled', 'throttling',
        '429', 'status_code=429'
    ]
    
    # Temporary network/server errors
    temporary_error_indicators = [
        'timeout', 'connection', 'network',
        'temporary', 'temporarily',
        '502', '503', '504',
        'bad gateway', 'service unavailable', 'gateway timeout',
        'internal server error', '500'
    ]
    
    # Check for retryable error patterns
    for indicator in rate_limit_indicators + temporary_error_indicators:
        if indicator in error_str:
            return True
    
    return False


def extract_retry_after(error: Exception) -> Optional[float]:
    """Extract retry-after delay from error message or headers"""
    error_str = str(error)
    
    # Look for retry-after patterns in error message
    import re
    
    # Pattern: "retry after X seconds"
    match = re.search(r'retry.*?after.*?(\d+(?:\.\d+)?)', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # Pattern: "wait X seconds"
    match = re.search(r'wait.*?(\d+(?:\.\d+)?)\s*seconds?', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # Pattern: "try again in X minutes"
    match = re.search(r'try.*?again.*?in.*?(\d+(?:\.\d+)?)\s*minutes?', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1)) * 60
    
    return None


async def retry_with_backoff(
    func,
    *args,
    retry_config: RetryConfig = None,
    console: Console = None,
    prompt_info: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute a function with retry logic and exponential backoff
    
    Args:
        func: The function to execute
        *args: Arguments for the function
        retry_config: Configuration for retry behavior
        console: Console for logging
        prompt_info: Information about the prompt being processed
        **kwargs: Keyword arguments for the function
    
    Returns:
        Result dictionary with success/error information
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    if console is None:
        console = Console()
    
    last_error = None
    
    for attempt in range(retry_config.max_retries + 1):
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # If we get here, the function succeeded
            if attempt > 0:
                console.print(f"[green]✓ Retry successful after {attempt} attempt(s)[/]")
            
            return {
                "success": True,
                "result": result,
                "attempts": attempt + 1
            }
            
        except Exception as e:
            last_error = e
            
            # Check if this is the last attempt
            if attempt >= retry_config.max_retries:
                break
            
            # Check if the error is retryable
            if not is_retryable_error(e):
                # Non-retryable error, fail immediately
                break
            
            # Calculate delay
            suggested_delay = extract_retry_after(e)
            delay = retry_config.get_delay(attempt, suggested_delay)
            
            # Log the retry attempt
            error_type = "Rate limit" if any(x in str(e).lower() for x in ['rate limit', '429']) else "Error"
            if prompt_info:
                console.print(f"[yellow]{error_type} for {prompt_info}: {str(e)[:100]}...[/]")
            else:
                console.print(f"[yellow]{error_type}: {str(e)[:100]}...[/]")
            
            console.print(f"[cyan]Retrying in {delay:.1f} seconds (attempt {attempt + 1}/{retry_config.max_retries + 1})[/]")
            
            # Wait before retrying
            await asyncio.sleep(delay)
    
    # All retries exhausted
    console.print(f"[red]All retry attempts exhausted. Final error: {str(last_error)[:100]}...[/]")
    
    return {
        "success": False,
        "error": str(last_error),
        "attempts": retry_config.max_retries + 1,
        "error_type": "retryable" if is_retryable_error(last_error) else "non_retryable"
    }


class BenchmarkCommands:
    """Main command class for benchmark operations"""

    def __init__(self, db, config):
        """Initialize benchmark commands with external dependencies"""
        self.db = db
        self.config = config
        self.console = Console()
        self.backup_manager = BackupManager()
        self.ui = BenchmarkUI(console=self.console, db=self.db, backup_manager=self.backup_manager)
        # Pass verbose parameter based on config
        verbose = config.get('verbose', False) if config else False
        self.results_viewer = ResultsViewer(
            db=self.db, console=self.console, verbose=verbose)

        # Initialize Kubernetes benchmark manager
        self.k8s_manager = KubernetesBenchmarkManager(
            console=self.console,
            backup_manager=self.backup_manager,
            verbose=verbose
        )

        # Make sure any other path references use Path.home()
        self.benchmark_dir = Path.home() / "dravik" / "benchmarks"
        
        # Initialize centralized API key manager
        try:
            from utils.api_key_manager import ApiKeyManager
            self.api_key_manager = ApiKeyManager()
        except ImportError:
            self.console.print("[yellow]Warning: Could not import ApiKeyManager, falling back to legacy API key handling[/]")
            self.api_key_manager = None
            # Store for API keys during the session (legacy fallback)
            self.session_api_keys = {}
        
        # Load any stored API keys at startup
        try:
            self._load_stored_api_keys()
        except Exception:
            # Silently fail if we can't load keys
            pass
        
    def _load_stored_api_keys(self):
        """Load stored API keys using the centralized API key manager"""
        try:
            if self.api_key_manager:
                # Use the centralized API key manager
                # It automatically loads keys and sets environment variables
                self.console.print("[dim]Loading API keys from centralized manager...[/]")
            else:
                # Legacy fallback: Load directly from JSON file
                keys_path = Path.home() / "dravik" / "config" / "api_keys.json"
                
                if keys_path.exists():
                    with open(keys_path, 'r') as f:
                        stored_keys = json.load(f)
                        self.session_api_keys = stored_keys
                        
                    # Set environment variables for retrieved keys
                    for key_name, key_value in self.session_api_keys.items():
                        if key_value and not os.environ.get(key_name):
                            os.environ[key_name] = key_value
        except Exception as e:
            # Silently fail if loading fails
            pass
            
    def _store_api_key(self, key_name, key_value):
        """Store API key using the centralized API key manager"""
        if not key_value:
            return False
            
        try:
            if self.api_key_manager:
                # Use the centralized API key manager
                success = self.api_key_manager.store_key(key_name, key_value)
                if success:
                    self.console.print(f"[green]✓ API key for {key_name} stored successfully[/]")
                return success
            else:
                # Legacy fallback: Store directly to JSON file
                config_dir = Path.home() / "dravik" / "config"
                config_dir.mkdir(parents=True, exist_ok=True)
                keys_path = config_dir / "api_keys.json"
                
                # Update session API keys
                self.session_api_keys[key_name] = key_value
                
                # Set environment variable
                os.environ[key_name] = key_value
                
                # Store to disk
                with open(keys_path, 'w') as f:
                    json.dump(self.session_api_keys, f)
                    
                return True
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not store API key: {str(e)}[/]")
            return False
            
    def _get_api_key(self, key_name, prompt_message=None):
        """Get API key using the centralized API key manager"""
        try:
            if self.api_key_manager:
                # Use the centralized API key manager
                api_key = self.api_key_manager.get_key(key_name)
                
                # If not found and prompt message is provided, ask user
                if not api_key and prompt_message:
                    self.console.print(f"[yellow]API key for {key_name} not found in settings[/]")
                    api_key_option = [
                        inquirer.Text(
                            'api_key',
                            message=prompt_message,
                            validate=lambda _, x: len(x.strip()) > 0
                        )
                    ]
                    
                    api_key_answer = inquirer.prompt(api_key_option)
                    if api_key_answer:
                        api_key = api_key_answer.get('api_key', '').strip()
                        if api_key:
                            # Store the key for future use
                            self._store_api_key(key_name, api_key)
                
                return api_key
            else:
                # Legacy fallback: Check environment, then session, then prompt
                api_key = os.environ.get(key_name)
                
                # If not in environment, check session
                if not api_key and hasattr(self, 'session_api_keys') and key_name in self.session_api_keys:
                    api_key = self.session_api_keys[key_name]
                    if api_key:
                        os.environ[key_name] = api_key
                
                # If still not found and prompt message is provided, ask user
                if not api_key and prompt_message:
                    self.console.print(f"[yellow]API key for {key_name} not found[/]")
                    api_key_option = [
                        inquirer.Text(
                            'api_key',
                            message=prompt_message,
                            validate=lambda _, x: len(x.strip()) > 0
                        )
                    ]
                    
                    api_key_answer = inquirer.prompt(api_key_option)
                    if api_key_answer:
                        api_key = api_key_answer.get('api_key', '').strip()
                        if api_key:
                            # Store the key for future use
                            self._store_api_key(key_name, api_key)
                
                return api_key
        except Exception as e:
            self.console.print(f"[yellow]Warning: Error retrieving API key: {str(e)}[/]")
            return None

    def run_benchmarks(self, dataset: Optional[Dict[str, Any]] = None):
        """Handle benchmark workflow with backup support"""
        try:
            # Check for existing sessions
            sessions = self.backup_manager.list_sessions()
            if sessions and self.ui.should_resume_session():
                session = self.ui.select_session(sessions)
                if session:
                    # Check if this is a Kubernetes session
                    if session.get("stage") == "kubernetes_running":
                        self._resume_kubernetes_benchmark(session)
                        return
                    else:
                        self._run_api_benchmark(
                            resume_session=session["session_id"])
                        return

            # Normal benchmark flow
            benchmark_type = self.ui.get_benchmark_type()
            if not benchmark_type:
                return
            
            # Special case: Custom HuggingFace dataset path
            if benchmark_type == "custom_hf_dataset":
                # Ask the user for the HuggingFace dataset path
                from rich.prompt import Prompt
                hf_dataset_path = Prompt.ask("Enter HuggingFace dataset path (e.g., 'databricks/databricks-dolly-15k')")
                
                if not hf_dataset_path:
                    self.console.print("[yellow]No dataset path provided. Exiting benchmark.[/yellow]")
                    return
                
                # Ask which field contains the prompts
                self.console.print("[bold cyan]Loading dataset information...[/bold cyan]")
                
                try:
                    from utils.hf_utils import load_dataset, get_dataset_config_names
                    
                    # Check if the dataset has multiple configurations
                    try:
                        configs = get_dataset_config_names(hf_dataset_path)
                        if configs and len(configs) > 0:
                            self.console.print(f"[cyan]Dataset has multiple configurations: {', '.join(configs)}[/cyan]")
                            config_name = Prompt.ask("Enter configuration name (or press Enter for default)", default=configs[0])
                            # Load a sample of the dataset to inspect its structure
                            dataset_sample = load_dataset(hf_dataset_path, name=config_name, split="train", streaming=True)
                        else:
                            # Load a sample of the dataset to inspect its structure
                            dataset_sample = load_dataset(hf_dataset_path, split="train", streaming=True)
                    except Exception as e:
                        self.console.print(f"[yellow]Error checking configurations: {str(e)}. Trying without configuration.[/yellow]")
                        # Load a sample of the dataset to inspect its structure
                        dataset_sample = load_dataset(hf_dataset_path, split="train", streaming=True)
                    
                    # Get the first example to inspect fields
                    example = next(iter(dataset_sample))
                    
                    # Display the available fields
                    self.console.print("[bold cyan]Dataset fields:[/bold cyan]")
                    for field in example.keys():
                        self.console.print(f"  - {field}")
                    
                    # Ask which field contains the prompts
                    prompt_field = Prompt.ask("Which field contains the prompts?")
                    
                    if prompt_field not in example.keys():
                        self.console.print(f"[red]Error: Field '{prompt_field}' not found in dataset.[/red]")
                        return
                        
                    # Get model configuration using the same UI as internal datasets
                    self.console.print("[bold cyan]Model Configuration[/bold cyan]")
                    
                    # Use the existing model selection UI
                    selected_models = self.ui.get_model_types_for_benchmark()
                    if not selected_models:
                        self.console.print("[yellow]No models selected. Cancelling benchmark.[/yellow]")
                        return
                    
                    # Get other parameters using the same UI pattern as internal datasets
                    params_questions = [
                        inquirer.Text(
                            'max_samples',
                            message="Maximum number of samples to process",
                            default="100",
                            validate=lambda _, x: x.lower() == 'all' or (x.isdigit() and int(x) > 0)
                        ),
                        inquirer.Text(
                            'concurrency',
                            message="Concurrency (number of simultaneous requests)",
                            default="3",
                            validate=lambda _, x: x.isdigit() and int(x) > 0 and int(x) <= 20
                        ),
                        inquirer.Text(
                            'max_tokens',
                            message="Maximum response tokens",
                            default="1000",
                            validate=lambda _, x: x.isdigit() and int(x) > 0
                        ),
                        inquirer.Text(
                            'max_retries',
                            message="Maximum retries for rate limits/errors (0-10)",
                            default="3",
                            validate=lambda _, x: x.isdigit() and 0 <= int(x) <= 10
                        ),
                        inquirer.Text(
                            'retry_delay',
                            message="Base retry delay in seconds (1-30)",
                            default="2",
                            validate=lambda _, x: x.replace('.', '', 1).isdigit() and 1 <= float(x) <= 30
                        )
                    ]
                    
                    # Only prompt for temperature if an Ollama model is selected
                    has_ollama = any((isinstance(m, str) and m.startswith('ollama:')) or (isinstance(m, dict) and (m.get('provider') == 'ollama' or m.get('type') == 'ollama')) for m in selected_models)
                    if has_ollama:
                        params_questions.append(
                            inquirer.Text(
                                'temperature',
                                message="Temperature (0.0-1.0)",
                                default="0.7",
                                validate=lambda _, x: (x.replace('.', '', 1).isdigit() and float(x) >= 0 and float(x) <= 1)
                            )
                        )
                    
                    params_answer = inquirer.prompt(params_questions)
                    if not params_answer:
                        return
                    
                    # Parse parameters
                    max_samples = params_answer['max_samples']
                    if max_samples.lower() == 'all':
                        max_samples = None
                    else:
                        max_samples = int(max_samples)
                    
                    concurrency = int(params_answer['concurrency'])
                    max_tokens = int(params_answer['max_tokens'])
                    temperature = float(params_answer.get('temperature', 0.7)) if has_ollama else None
                    max_retries = int(params_answer['max_retries'])
                    retry_delay = float(params_answer['retry_delay'])
                    
                    # Process the dataset and send prompts to the target models
                    self.console.print("[bold green]Starting static scan with custom dataset...[/bold green]")
                    
                    # Create a results directory for this run
                    import uuid
                    run_id = str(uuid.uuid4())[:8]
                    results_dir = f"custom_dataset_results_{run_id}"
                    os.makedirs(results_dir, exist_ok=True)
                    
                    # Create a table to display results
                    from rich.table import Table
                    from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
                    
                    # Import necessary modules for target model interaction
                    from benchmark.conversation_red_teaming import query_target_model
                    from benchmarks.api.openai_handler import OpenAIHandler
                    from benchmarks.api.gemini_handler import GeminiHandler
                    from benchmarks.models.handlers.ollama_handler import OllamaHandler
                    
                    # Prepare dataset iterator
                    if configs and len(configs) > 0 and 'config_name' in locals():
                        dataset_iter = load_dataset(hf_dataset_path, name=config_name, split="train", streaming=True)
                    else:
                        dataset_iter = load_dataset(hf_dataset_path, split="train", streaming=True)
                    
                    # Ask the user how many samples to load
                    from rich.prompt import IntPrompt, Prompt
                    
                    sample_count_question = [
                        inquirer.List(
                            'sample_option',
                            message="How many prompts would you like to process?",
                            choices=[
                                ('All available prompts', 'all'),
                                ('Specific number of prompts', 'specific'),
                                ('Cancel', None)
                            ]
                        )
                    ]
                    
                    sample_count_answer = inquirer.prompt(sample_count_question)
                    if not sample_count_answer or sample_count_answer['sample_option'] is None:
                        return
                        
                    if sample_count_answer['sample_option'] == 'specific':
                        max_samples = IntPrompt.ask("Enter the number of prompts to process", default=100)
                    else:  # 'all'
                        max_samples = None
                    
                    # Convert dataset to a list of samples up to max_samples
                    samples = []
                    count = 0
                    
                    # Create a panel for the dataset loading status
                    from rich.panel import Panel
                    from rich.live import Live
                    from rich.table import Table
                    from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
                    
                    progress = Progress(
                        TextColumn("[bold blue]{task.description}"),
                        BarColumn(),
                        TaskProgressColumn(),
                    )
                    
                    loading_task = progress.add_task("[cyan]Loading dataset samples...", total=None)
                    
                    # Create a panel to display the loading progress
                    def get_loading_panel():
                        return Panel(
                            progress,
                            title=f"Loading Dataset: {hf_dataset_path}",
                            border_style="cyan",
                            padding=(1, 2)
                        )
                    
                    # Display the loading progress in a live panel
                    with Live(get_loading_panel(), refresh_per_second=4) as live:
                        for item in dataset_iter:
                            if max_samples is not None and count >= max_samples:
                                break
                                
                            # Get the prompt from the specified field
                            prompt = item.get(prompt_field, "")
                            if not prompt:
                                continue
                                
                            samples.append(prompt)
                            count += 1
                            
                            # Update progress
                            progress.update(loading_task, description=f"[cyan]Loaded {count} samples...")
                            
                            # Update the live display
                            live.update(get_loading_panel())
                    
                    self.console.print(f"[bold green]✓ Loaded {len(samples)} samples from dataset[/bold green]")
                    
                    # Create UI components for the benchmark display
                    from rich.panel import Panel
                    from rich.live import Live
                    from rich.table import Table
                    from rich.layout import Layout
                    from rich.console import Group
                    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
                    
                    # Create the main layout
                    layout = Layout()
                    layout.split_column(
                        Layout(name="progress_section"),
                        Layout(name="details_section")
                    )
                    
                    # Create a progress bar for overall completion
                    benchmark_progress = Progress(
                        TextColumn("[bold cyan]Benchmark in Progress"),
                        BarColumn(bar_width=None, style="magenta", complete_style="magenta"),
                        TextColumn("[bold]{task.percentage:.0f}% Completed: {task.completed}/{task.total}"),
                        TextColumn("[bold]{task.elapsed}"),
                        expand=True
                    )
                    
                    # Add a task for overall progress
                    overall_task_id = benchmark_progress.add_task("Benchmark Progress", total=len(samples))
                    
                    # Create a table for the prompts and their status
                    prompts_table = Table(show_header=True, header_style="bold", box=None)
                    prompts_table.add_column("Prompt", style="white", width=60, no_wrap=False)
                    prompts_table.add_column("Status", style="green", width=20)
                    prompts_table.add_column("Time", style="cyan", width=10)
                    
                    # Create a table for model results
                    models_table = Table(show_header=True, header_style="bold", box=None)
                    models_table.add_column("Model", style="cyan")
                    models_table.add_column("Progress", style="green")
                    models_table.add_column("Status", style="yellow")
                    
                    # Function to update the benchmark display
                    def get_benchmark_display():
                        # Create the progress section
                        progress_panel = Panel(
                            benchmark_progress,
                            title="Benchmark Progress",
                            border_style="cyan",
                            padding=(1, 2)
                        )
                        
                        # Create the details section with model info
                        current_model_display = "Initializing..."
                        if 'current_model_type' in locals() and 'current_model_id' in locals():
                            current_model_display = f"{current_model_type.capitalize()}: {current_model_id}"
                        elif selected_models:
                            # Fallback to first selected model
                            model = selected_models[0]
                            if isinstance(model, str):
                                if model.startswith('ollama:'):
                                    model_type = 'ollama'
                                    model_id = model.split(':', 1)[1]
                                else:
                                    model_type = 'openai'
                                    model_id = model
                            else:
                                model_type = model.get('type') or model.get('provider', 'openai')
                                model_id = model.get('id') or model.get('model', 'gpt-3.5-turbo')
                            current_model_display = f"{model_type.capitalize()}: {model_id}"
                        
                        # Create the details panel with safe table handling
                        try:
                            # Create a new table each time to avoid race conditions
                            display_table = Table(show_header=True, header_style="bold", box=None)
                            display_table.add_column("Prompt", style="white", width=60, no_wrap=False)
                            display_table.add_column("Status", style="green", width=20)
                            display_table.add_column("Time", style="cyan", width=10)
                            
                            # Safely copy current batch data if available
                            if 'batch_prompt_data' in locals() and batch_prompt_data:
                                for i, display_prompt in enumerate(batch_prompt_data):
                                    status = "Processing"
                                    time_str = "-"
                                    
                                    # Check if this prompt has been processed
                                    if 'processed_count' in locals() and i < processed_count:
                                        status = "Completed"
                                        time_str = "Done"
                                    elif 'error_count' in locals() and i < error_count:
                                        status = "Error"
                                        time_str = "Error"
                                    
                                    display_table.add_row(display_prompt, status, time_str)
                            else:
                                # Show a placeholder if no data is available
                                display_table.add_row("Preparing prompts...", "Initializing", "-")
                            
                            display_content = display_table
                            
                        except Exception as table_error:
                            # Fallback to simple text if table creation fails
                            display_content = "[dim]Processing prompts...[/dim]"
                        
                        # Create the details panel
                        try:
                            details_panel = Panel(
                                Group(
                                    f"[bold green]{current_model_display}[/bold green]",
                                    "Status: Running",
                                    display_content
                                ),
                                border_style="green",
                                padding=(1, 1)
                            )
                        except Exception as panel_error:
                            # Fallback panel if there are any issues
                            details_panel = Panel(
                                f"[bold green]{current_model_display}[/bold green]\nStatus: Running\nProcessing prompts...",
                                border_style="green",
                                padding=(1, 1)
                            )
                        
                        # Update the layout sections
                        try:
                            layout["progress_section"].update(progress_panel)
                            layout["details_section"].update(details_panel)
                        except Exception as layout_error:
                            # If layout update fails, create a simple fallback
                            pass
                        
                        return layout
                    
                    # Process with the live benchmark display
                    with Live(get_benchmark_display(), refresh_per_second=4) as live:
                        # Process each model
                        for model in selected_models:
                            # Determine model type and ID
                            if isinstance(model, str):
                                if model.startswith('ollama:'):
                                    model_type = 'ollama'
                                    model_id = model.split(':', 1)[1]
                                else:
                                    # Assume OpenAI model if no prefix
                                    model_type = 'openai'
                                    model_id = model
                            else:
                                # Handle dictionary format
                                model_type = model.get('type') or model.get('provider', 'openai')
                                model_id = model.get('id') or model.get('model', 'gpt-3.5-turbo')
                            
                            # Create a results file for this model
                            results_file = os.path.join(results_dir, f"{model_type}_{model_id}_results.jsonl")
                            
                            # Clear the prompts table for this model
                            # prompts_table.rows = []  # Commented out to prevent race condition
                            
                            # Update the details panel with the current model info
                            details_panel = Panel(
                                Group(
                                    f"[bold green]{model_type.capitalize()}: {model_id}[/bold green]",
                                    "Status: Running",
                                    "Processing prompts..."
                                ),
                                border_style="green",
                                padding=(1, 1)
                            )
                            
                            # Update the layout
                            layout["details_section"].update(details_panel)
                            
                            # Update the live display
                            live.update(get_benchmark_display())
                            
                            # Process samples with concurrency and retry logic
                            import asyncio
                            from concurrent.futures import ThreadPoolExecutor
                            
                            # Create retry configuration for this benchmark
                            retry_config = RetryConfig(
                                max_retries=max_retries,  # Use user-configured retries
                                base_delay=retry_delay,  # Use user-configured base delay
                                max_delay=120.0,  # Max 2 minutes delay
                                exponential_base=2.0,  # Double delay each time
                                jitter=True  # Add randomness to prevent thundering herd
                            )
                            
                            # Define async wrapper for query_target_model
                            async def query_with_retry(prompt, model_type, model_id, **kwargs):
                                """Wrapper to add retry logic to query_target_model"""
                                def sync_query():
                                    return query_target_model(prompt, model_type, model_id, **kwargs)
                                
                                prompt_preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
                                result = await retry_with_backoff(
                                    sync_query,
                                    retry_config=retry_config,
                                    console=self.console,
                                    prompt_info=f"prompt '{prompt_preview}'"
                                )
                                
                                if result["success"]:
                                    return result["result"]
                                else:
                                    # Convert retry failure to exception for consistent error handling
                                    raise Exception(f"Failed after {result['attempts']} attempts: {result['error']}")
                            
                            # Create a thread pool for concurrent requests
                            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                                # Process samples in batches
                                batch_size = min(concurrency, len(samples))
                                processed_count = 0
                                error_count = 0
                                retry_count = 0
                                
                                # Track current model for display
                                current_model_type = model_type
                                current_model_id = model_id
                                
                                for i in range(0, len(samples), batch_size):
                                    batch = samples[i:i+batch_size]
                                    batch_results = []
                                    
                                    # Store original prompt data for updating status
                                    batch_prompt_data = []
                                    
                                    # Add the current batch of prompts to the table with 'Processing' status
                                    for j, prompt in enumerate(batch):
                                        # Truncate prompt for display if too long
                                        display_prompt = prompt[:57] + "..." if len(prompt) > 60 else prompt
                                        batch_prompt_data.append(display_prompt)
                                    
                                    # Update display without modifying shared table
                                    try:
                                        live.update(get_benchmark_display())
                                    except Exception as display_error:
                                        # Continue without display updates if there's an error
                                        pass
                                    
                                    # Process batch concurrently with retry logic
                                    async def process_batch_async():
                                        """Process a batch of prompts asynchronously with retry logic"""
                                        tasks = []
                                        
                                        for j, prompt in enumerate(batch):
                                            task = asyncio.create_task(
                                                query_with_retry(
                                                    prompt, 
                                                    model_type, 
                                                    model_id,
                                                    max_tokens=max_tokens,
                                                    temperature=temperature if model_type == 'ollama' else None
                                                )
                                            )
                                            tasks.append((j, prompt, task))
                                        
                                        # Wait for all tasks to complete
                                        batch_results = []
                                        for j, prompt, task in tasks:
                                            start_time = datetime.now()
                                            try:
                                                response = await task
                                                batch_results.append({
                                                    "prompt": prompt,
                                                    "response": response,
                                                    "model": f"{model_type}/{model_id}",
                                                    "success": True,
                                                    "response_time": (datetime.now() - start_time).total_seconds()
                                                })
                                                processed_count += 1
                                            except Exception as e:
                                                error_type = "retryable" if is_retryable_error(e) else "non_retryable"
                                                
                                                if is_retryable_error(e):
                                                    # This was a retryable error that still failed after retries
                                                    retry_count += 1
                                                    self.console.print(f"[red]Failed after retries: {str(e)[:100]}...[/]")
                                                
                                                batch_results.append({
                                                    "prompt": prompt,
                                                    "error": str(e),
                                                    "model": f"{model_type}/{model_id}",
                                                    "success": False,
                                                    "error_type": error_type,
                                                    "response_time": (datetime.now() - start_time).total_seconds()
                                                })
                                                error_count += 1
                                            
                                            # Update overall progress
                                            benchmark_progress.update(overall_task_id, advance=1)
                                            
                                            # Update display safely
                                            try:
                                                live.update(get_benchmark_display())
                                            except Exception as display_error:
                                                # Continue without display updates if there's an error
                                                pass
                                        
                                        return batch_results
                                    
                                    # Run the async batch processing
                                    try:
                                        batch_results = asyncio.run(process_batch_async())
                                    except Exception as batch_error:
                                        self.console.print(f"[red]Error processing batch: {str(batch_error)}[/]")
                                        # Create error results for the entire batch
                                        batch_results = []
                                        for prompt in batch:
                                            batch_results.append({
                                                "prompt": prompt,
                                                "error": str(batch_error),
                                                "model": f"{model_type}/{model_id}",
                                                "success": False,
                                                "error_type": "batch_processing_error"
                                            })
                                            error_count += 1
                                    
                                    # Save batch results
                                    with open(results_file, "a") as f:
                                        for result in batch_results:
                                            json.dump(result, f)
                                            f.write("\n")
                                
                                # Log retry statistics
                                if retry_count > 0:
                                    self.console.print(f"[yellow]Note: {retry_count} prompts required retries due to rate limits or temporary errors[/]")
                                
                                # Display final statistics for this model
                                total_processed = processed_count + error_count
                                success_rate = (processed_count / total_processed * 100) if total_processed > 0 else 0
                                self.console.print(f"[cyan]Model {model_type}/{model_id}: {processed_count}/{total_processed} successful ({success_rate:.1f}%)[/]")
                    
                    # Create a summary panel for the completed benchmark
                    from rich.panel import Panel
                    from rich.console import Group
                    from rich.table import Table
                    
                    # Create a summary table for the benchmark results
                    summary_table = Table(show_header=True, header_style="bold")
                    summary_table.add_column("Model", style="cyan")
                    summary_table.add_column("Processed", style="green")
                    summary_table.add_column("Errors", style="red")
                    summary_table.add_column("Time", style="yellow")
                    
                    # Calculate total elapsed time
                    elapsed = benchmark_progress.tasks[overall_task_id].elapsed
                    elapsed_str = str(timedelta(seconds=int(elapsed)))
                    
                    # Add a row for each model
                    for model in selected_models:
                        # Determine model type and ID
                        if isinstance(model, str):
                            if model.startswith('ollama:'):
                                model_type = 'ollama'
                                model_id = model.split(':', 1)[1]
                            else:
                                model_type = 'openai'
                                model_id = model
                        else:
                            model_type = model.get('type') or model.get('provider', 'openai')
                            model_id = model.get('id') or model.get('model', 'gpt-3.5-turbo')
                            
                        # Get the results file path
                        results_file = os.path.join(results_dir, f"{model_type}_{model_id}_results.jsonl")
                        
                        # Count successful and error responses
                        success_count = 0
                        error_count = 0
                        if os.path.exists(results_file):
                            with open(results_file, 'r') as f:
                                for line in f:
                                    try:
                                        result = json.loads(line)
                                        if "error" in result:
                                            error_count += 1
                                        else:
                                            success_count += 1
                                    except:
                                        pass
                        
                        # Add to summary table
                        summary_table.add_row(
                            f"{model_type}/{model_id}",
                            str(success_count),
                            str(error_count),
                            elapsed_str
                        )
                    
                    # Create a final results panel with benchmark statistics
                    benchmark_stats = Panel(
                        Group(
                            f"[bold cyan]Benchmark Complete[/bold cyan]",
                            f"[bold]Dataset:[/bold] {hf_dataset_path}",
                            f"[bold]Prompt Field:[/bold] {prompt_field}",
                            f"[bold]Sample Count:[/bold] {len(samples)}",
                            f"[bold]Total Time:[/bold] {elapsed_str}",
                            f"[bold]Results Directory:[/bold] {results_dir}"
                        ),
                        title="Benchmark Statistics",
                        border_style="cyan",
                        padding=(1, 2)
                    )
                    
                    # Create a summary panel with the benchmark results
                    summary_panel = Panel(
                        Group(
                            benchmark_stats,
                            "",  # Empty line for spacing
                            summary_table
                        ),
                        title=f"Custom Dataset Scan Results",
                        border_style="green",
                        padding=(1, 2)
                    )
                    
                    # Display summary
                    self.console.print(summary_panel)
                    
                    # Display success message
                    self.console.print(f"[bold green]✓ Successfully processed {len(samples)} samples from {hf_dataset_path}[/bold green]")
                    self.console.print(f"[bold cyan]Results saved to directory: {results_dir}[/bold cyan]")
                    
                    # Save the dataset to the database for future use
                    try:
                        self.console.print("[cyan]Saving dataset to database for future use...[/cyan]")
                        
                        # Create a unique dataset name from the HuggingFace path
                        safe_dataset_name = hf_dataset_path.replace('/', '_').replace('-', '_')
                        
                        # Prepare dataset data structure similar to the dataset command
                        dataset_data = {
                            'name': safe_dataset_name,
                            'format_type': 'huggingface',
                            'examples': [{'prompt': sample} for sample in samples],
                            '_metadata': {
                                'id': str(uuid.uuid4()),
                                'source': hf_dataset_path,
                                'prompt_field': prompt_field,
                                'download_date': datetime.now().isoformat(),
                                'type': 'huggingface',
                                'format': 'custom_scan',
                                'sample_count': len(samples),
                                'description': f"Dataset from {hf_dataset_path} used in static scan"
                            }
                        }
                        
                        # Save to HuggingFace datasets table
                        hf_success = self.db.save_huggingface_dataset(
                            dataset_name=safe_dataset_name,
                            dataset_id=dataset_data['_metadata']['id'],
                            data=dataset_data
                        )
                        
                        if hf_success:
                            self.console.print(f"[green]✓ Dataset '{safe_dataset_name}' saved to database and can be reused for future benchmarks[/green]")
                        else:
                            self.console.print("[yellow]Warning: Could not save dataset to database[/yellow]")
                            
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not save dataset to database: {str(e)}[/yellow]")
                    
                    # Save results to database
                    try:
                        # Create a results structure for database storage
                        benchmark_results = {
                            "benchmark_id": str(uuid.uuid4()),
                            "timestamp": datetime.now().isoformat(),
                            "dataset": {
                                "name": hf_dataset_path,
                                "type": "custom_huggingface",
                                "prompt_field": prompt_field,
                                "sample_count": len(samples)
                            },
                            "models_tested": [
                                f"{model.get('type', 'unknown')}/{model.get('id', 'unknown')}" 
                                if isinstance(model, dict) else model 
                                for model in selected_models
                            ],
                            "results_directory": results_dir,
                            "execution_time": elapsed_str,
                            "summary": {
                                "total_samples": len(samples),
                                "models_tested": len(selected_models),
                                "results_per_model": []
                            }
                        }
                        
                        # Add per-model results to summary
                        for model in selected_models:
                            if isinstance(model, dict):
                                model_type = model.get('type') or model.get('provider', 'openai')
                                model_id = model.get('id') or model.get('model', 'gpt-3.5-turbo')
                            else:
                                if model.startswith('ollama:'):
                                    model_type = 'ollama'
                                    model_id = model.split(':', 1)[1]
                                else:
                                    model_type = 'openai'
                                    model_id = model
                            
                            # Get the results file path
                            results_file = os.path.join(results_dir, f"{model_type}_{model_id}_results.jsonl")
                            
                            # Count successful and error responses
                            success_count = 0
                            error_count = 0
                            if os.path.exists(results_file):
                                with open(results_file, 'r') as f:
                                    for line in f:
                                        try:
                                            result = json.loads(line)
                                            if "error" in result:
                                                error_count += 1
                                            else:
                                                success_count += 1
                                        except:
                                            pass
                            
                            benchmark_results["summary"]["results_per_model"].append({
                                "model": f"{model_type}/{model_id}",
                                "success_count": success_count,
                                "error_count": error_count,
                                "success_rate": f"{(success_count / len(samples) * 100):.1f}%" if len(samples) > 0 else "0%"
                            })
                        
                        # Save to database using the existing method
                        save_success = self._save_api_benchmark_results(
                            benchmark_results, 
                            dataset_name=hf_dataset_path
                        )
                        
                        if save_success:
                            self.console.print("[green]✓ Results saved to database[/]")
                        else:
                            self.console.print("[yellow]Warning: Could not save results to database[/]")
                            
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not save results to database: {str(e)}[/]")
                        import traceback
                        traceback.print_exc()
                    
                    return
                    
                except Exception as e:
                    self.console.print(f"[red]Error processing custom dataset: {str(e)}[/red]")
                    import traceback
                    traceback.print_exc()
                    return

            # Special case: External dataset benchmarking
            if benchmark_type == "external_dataset":
                # Have the user select a dataset if not provided
                if not dataset:
                    from ..dataset.command import DatasetCommands
                    dataset_commands = DatasetCommands(self.db)
                    dataset = dataset_commands.select_dataset_for_benchmarking()
                    if not dataset:
                        self.console.print(
                            "[yellow]No dataset selected. Exiting benchmark.[/]")
                        return

                # Now that we have a dataset, get comprehensive configuration using the same UI as other benchmarks
                self.console.print(
                    f"[cyan]Selected dataset: {dataset.get('name', 'Unknown')}[/]")

                # Use the same comprehensive model selection as internal datasets
                self.console.print("[bold cyan]Model Configuration[/bold cyan]")
                
                # Use the existing comprehensive model selection UI
                selected_models = self.ui.get_model_types_for_benchmark()
                if not selected_models:
                    self.console.print("[yellow]No models selected. Cancelling benchmark.[/yellow]")
                    return
                
                # Get other parameters using the same UI pattern as internal datasets
                params_questions = [
                    inquirer.Text(
                        'concurrency',
                        message="Concurrency (number of simultaneous requests)",
                        default="3",
                        validate=lambda _, x: x.isdigit() and int(x) > 0 and int(x) <= 20
                    ),
                    inquirer.Text(
                        'max_tokens',
                        message="Maximum response tokens",
                        default="1000",
                        validate=lambda _, x: x.isdigit() and int(x) > 0
                    )
                ]
                
                # Only prompt for temperature if an Ollama model is selected
                has_ollama = any((isinstance(m, str) and m.startswith('ollama:')) or (isinstance(m, dict) and (m.get('provider') == 'ollama' or m.get('type') == 'ollama')) for m in selected_models)
                if has_ollama:
                    params_questions.append(
                        inquirer.Text(
                            'temperature',
                            message="Temperature (0.0-1.0)",
                            default="0.7",
                            validate=lambda _, x: (x.replace('.', '', 1).isdigit() and float(x) >= 0 and float(x) <= 1)
                        )
                    )
                
                params_answer = inquirer.prompt(params_questions)
                if not params_answer:
                    self.console.print("[yellow]Configuration cancelled.[/yellow]")
                    return
                
                # Parse parameters
                concurrency = int(params_answer['concurrency'])
                max_tokens = int(params_answer['max_tokens'])
                temperature = float(params_answer.get('temperature', 0.7)) if has_ollama else 0.7
                
                # Ask about prompt count for the dataset
                self.console.print("[bold cyan]Dataset Processing Configuration[/bold cyan]")
                
                sample_count_question = [
                    inquirer.List(
                        'sample_option',
                        message="How many prompts would you like to process from this dataset?",
                        choices=[
                            ('All available prompts in the dataset', 'all'),
                            ('Specific number of prompts', 'specific'),
                            ('Cancel', None)
                        ]
                    )
                ]
                
                sample_count_answer = inquirer.prompt(sample_count_question)
                if not sample_count_answer or sample_count_answer['sample_option'] is None:
                    self.console.print("[yellow]Configuration cancelled.[/yellow]")
                    return
                    
                max_samples = None
                if sample_count_answer['sample_option'] == 'specific':
                    from rich.prompt import IntPrompt
                    max_samples = IntPrompt.ask("Enter the number of prompts to process", default=100)
                    if max_samples <= 0:
                        self.console.print("[yellow]Invalid number of prompts. Cancelling benchmark.[/yellow]")
                        return
                # else: max_samples remains None for 'all'
                
                # Create comprehensive config structure
                config = {
                    "models": selected_models,
                    "concurrency": concurrency,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "max_samples": max_samples  # Add max_samples to config
                }

                # Use kubernetes if requested
                use_kubernetes = self.ui.should_use_kubernetes()

                # Run the appropriate benchmark with the dataset
                if use_kubernetes:
                    self._run_api_benchmark_on_kubernetes(
                        dataset=dataset, config=config)
                else:
                    self._run_api_benchmark(dataset=dataset, config=config)
                return

            # Handle internal dataset case - dynamic or static
            if benchmark_type == "api":
                # Get the internal dataset configuration
                config = self.ui.get_internal_dataset_config()
                if not config:
                    return

                # Check if kubernetes should be used
                use_kubernetes = self.ui.should_use_kubernetes()

                # Run the benchmark with the configuration
                if use_kubernetes:
                    self._run_api_benchmark_on_kubernetes(config=config)
                else:
                    self._run_api_benchmark(config=config)
                return
            
            # For other benchmark types, continue with existing flow
            use_kubernetes = self.ui.should_use_kubernetes()
            
            # Print dataset info if provided
            if dataset:
                self.console.print(f"[cyan]Using dataset: {dataset.get('name', 'Unknown')}[/]")
                
            if benchmark_type == 'flexible':
                self._run_flexible_benchmark(dataset=dataset)
            elif benchmark_type == 'conversation_red_teaming':
                # Handle Conversation Red Teaming
                self.run_conversation_red_teaming()
            else:
                self._run_performance_benchmark(benchmark_type, dataset=dataset)
                
        except Exception as e:
            self.console.print(f"[bold red]Error in benchmarks: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _run_api_benchmark(self, config: Optional[Dict[str, Any]] = None, dataset: Optional[Dict[str, Any]] = None, resume_session: Optional[str] = None, provided_models: Optional[List[str]] = None):
        """Run API benchmark with provided configuration or interactive prompts"""
        try:
            # Use Kubernetes if configured
            if self.ui.should_use_kubernetes():
                return self._run_api_benchmark_on_kubernetes(config, dataset)
            
            # Note: APIBenchmarkRunner is already imported at the top of the file from .runners
            
            # Create default config if not provided
            benchmark_config = config or {}
            
            # Prepare model configurations if needed
            if benchmark_config and 'models' in benchmark_config:
                models = benchmark_config.get("models", [])
                max_tokens = benchmark_config.get("max_tokens", 1000)
                temperature = benchmark_config.get("temperature", 0.7)
                concurrency = benchmark_config.get("concurrency", 3)
                max_samples = benchmark_config.get("max_samples")  # Get max_samples from config
                
                # Import ModelLoader for custom model support
                from benchmarks.models.model_loader import ModelLoader
                model_loader = ModelLoader(verbose=False)
                
                # Prepare model configs
                model_configs = self._prepare_model_configs(models, model_loader, max_tokens, temperature)
                
                # Add max_samples to each model config if specified
                if max_samples is not None:
                    for config in model_configs:
                        config["max_samples"] = max_samples
            elif provided_models:
                # Use provided models directly, bypassing interactive selection
                self.console.print(f"[cyan]Using provided models: {', '.join(provided_models)}[/]")
                # Import ModelLoader for custom model support
                from benchmarks.models.model_loader import ModelLoader
                model_loader = ModelLoader(verbose=False)
                
                # Use default values for max_tokens and temperature
                max_tokens = 1000
                temperature = 0.7
                concurrency = 3
                
                # Prepare model configs using the provided models
                model_configs = self._prepare_model_configs(provided_models, model_loader, max_tokens, temperature)
            else:
                model_configs = []
                concurrency = 3
            
            # Create the benchmark runner with all required parameters
            runner = APIBenchmarkRunner(
                db=self.db,
                console=self.console,
                backup_manager=self.backup_manager,
                model_configs=model_configs,
                concurrency=concurrency,
                retry_config=RetryConfig(
                    max_retries=config.get('max_retries', 3),
                    base_delay=config.get('retry_delay', 2.0),
                    max_delay=120.0,
                    exponential_base=2.0,
                    jitter=True
                ) if config else RetryConfig()
            )
            
            # Verify API environment
            if not self._verify_api_environment():
                self.console.print("[yellow]API environment verification failed. Please fix the issues and try again.[/]")
                return
            
            # Use provided dataset or get internal dataset config
            if dataset:
                # Dataset provided externally, use it
                self.console.print(f"[cyan]Using provided dataset: {dataset.get('name', 'Custom Dataset')}[/]")
            else:
                # Try to get config from resume session or user input
                if resume_session:
                    config = resume_session.get('config')
                    self.console.print(f"[cyan]Resuming session with saved configuration[/]")
                elif not config:
                    self.console.print("[cyan]Setting up API benchmark configuration...[/]")
                    # Verify all API keys and inform user of missing ones
                    self._verify_all_api_keys()
                    # Get configuration interactively
                    config = self.ui.get_internal_dataset_config()
                
                if not config:
                    self.console.print("[yellow]Benchmark configuration cancelled.[/]")
                    return
                
                # Verify if selected models are available
                if not self._verify_model_availability(config):
                    return
                
                # Prepare dataset based on config
                dataset_type = config.get("dataset_type", "static")
                
                # Get prompt count
                prompt_count = config.get("prompt_count", 10)
                
                # Prepare API parameters
                max_tokens = config.get("max_tokens", 1000)
                temperature = config.get("temperature", 0.0)
                
                if dataset_type == "static":
                    # Generate advanced adversarial prompts using the user interface
                    self.console.print("[cyan]Generating adversarial prompts with multiple techniques...[/]")
                    
                    # Get target model context from config if available
                    target_model_context = config.get("target_model_context")
                    
                    # Import and use adversarial prompt generator
                    try:
                        from benchmarks.templates.advanced_jailbreak_templates import (
                            generate_adversarial_prompts,
                            get_template_categories,
                            get_technique_description
                        )
                        
                        # Always use Markov-based generation
                        use_markov = True
                        self.console.print(f"[cyan]Re-looking at it")
                        
                        # Import the markov jailbreak generator to use advanced templates
                        from benchmarks.templates.markov_jailbreak_generator import (
                            generate_diverse_adversarial_prompts
                        )
                        
                        # Show available techniques with descriptions
            
                        technique_categories = get_template_categories()
                
                        
                        # Automatically use all individual techniques (excluding ALL_TECHNIQUES itself)
                        all_individual_techniques = [t for t in technique_categories if t != "ALL_TECHNIQUES"]
                        selected_techniques = all_individual_techniques
                        
                        # Display which techniques will be used
                        
                        
                        # Show target model context if available
                        if target_model_context:
                            self.console.print("[bold cyan]Target Model Context:[/]")
                            if 'system_prompt' in target_model_context:
                                prompt_preview = target_model_context['system_prompt'][:100] + "..." if len(target_model_context['system_prompt']) > 100 else target_model_context['system_prompt']
                                self.console.print(f"  • [cyan]System Prompt:[/] {prompt_preview}")
                            if 'use_case' in target_model_context:
                                self.console.print(f"  • [cyan]Use Case:[/] {target_model_context['use_case']}")
                            if 'additional_details' in target_model_context:
                                details_preview = target_model_context['additional_details'][:100] + "..." if len(target_model_context['additional_details']) > 100 else target_model_context['additional_details']
                                self.console.print(f"  • [cyan]Additional Details:[/] {details_preview}")
                            self.console.print()
                        
                        # Generate prompts with Markov-based method and target context
                        if target_model_context:
                            self.console.print("[cyan]Refining prompts with target model context...[/]")
                        
                        verbose_mode = config.get("verbose", False)
                        
                        # Use the internal method with target model context
                        dataset = self._generate_markov_templates(
                            prompt_count=prompt_count,
                            verbose=verbose_mode,
                            model_name=config.get("validation_model", "gemini-1.5-flash"),
                            model_provider=config.get("model_provider", "gemini"),
                            target_model_context=target_model_context,
                            use_gemini_augmentation=config.get("job_type", "usecase_specific") == "usecase_specific"
                        )
                        
                        # Add generation method to metadata if not already present
                        if "metadata" not in dataset:
                            dataset["metadata"] = {}
                        dataset["metadata"]["generation_method"] = "markov"
                        dataset["metadata"]["generation_time"] = datetime.now().isoformat()
                        dataset["metadata"]["count"] = len(dataset["examples"])
                        
                        self.console.print(f"[green]✓ Generated {len(dataset['examples'])} adversarial prompts[/]")
                        
                        # Display a sample of the prompts
                        if len(dataset["examples"]) > 0:
                            self.console.print("\n[bold]Sample of generated prompts:[/]")
                            display_count = min(3, len(dataset["examples"]))
                            for i in range(display_count):
                                prompt = dataset["examples"][i].get("prompt", "")
                                truncated = prompt[:150] + "..." if len(prompt) > 150 else prompt
                                self.console.print(f"[cyan]{i+1}.[/] {truncated}")
                            self.console.print()
                            
                    except (ImportError, Exception) as e:
                        # If we hit an error, we show it but still try to use advanced templates without Markov
                        self.console.print(f"[yellow]Error with Markov generation: {str(e)}. Trying advanced templates directly.[/]")
                        
                        try:
                            # Try to use the advanced templates directly
                            from benchmarks.templates.advanced_jailbreak_templates import generate_adversarial_prompts
                            
                            # Generate prompts using advanced templates
                            prompts = generate_adversarial_prompts(count=prompt_count, techniques=None)
                            
                            # Create the dataset structure
                            dataset = {
                                "name": "Advanced Adversarial Templates",
                                "description": "Adversarial prompts generated using advanced jailbreak templates",
                                "examples": [{"prompt": prompt, "technique": "advanced", "category": "general"} for prompt in prompts],
                                "metadata": {
                                    "generator": "advanced_templates",
                                    "generation_time": datetime.now().isoformat(),
                                    "count": len(prompts)
                                }
                            }
                            
                            self.console.print(f"[green]✓ Generated {len(prompts)} adversarial prompts using advanced templates[/]")
                            
                        except (ImportError, Exception) as e:
                            # This is a true failure - show the error but don't stop execution
                            self.console.print(f"[red]Advanced templates not available: {str(e)}.[/]")
                            
                            # Create an empty dataset so the benchmark can continue
                            dataset = {
                                "name": "Empty Dataset",
                                "description": "No prompts could be generated",
                                "examples": []
                            }
                    
                elif dataset_type == "synthetic":
                    # Generate synthetic prompts using models
                    self.console.print("[cyan]Generating synthetic adversarial prompts using AI models...[/]")
                    from benchmarks.api.bypass_tester import BypassTester
                    tester = BypassTester(db=self.db, console=self.console, verbose=True)
                    prompts = tester.generate_test_prompts(num_prompts=prompt_count, force_templates=False)
                    
                    # Create a dataset structure
                    dataset = {
                        "name": "Generated Synthetic Adversarial Dataset",
                        "description": "Automatically generated dataset using AI models",
                        "examples": [{"prompt": prompt} for prompt in prompts]
                    }
                    
                    self.console.print(f"[green]✓ Generated {len(prompts)} synthetic adversarial prompts[/]")
                    
                elif dataset_type == "existing":
                    # Load an existing dataset
                    self.console.print("[cyan]Select an existing dataset to use:[/]")
                    from ..dataset.command import DatasetCommands
                    dataset_commands = DatasetCommands(self.db)
                    dataset = dataset_commands.select_dataset_for_benchmarking()
                    
                    if not dataset:
                        self.console.print("[yellow]No dataset selected. Cancelling benchmark.[/]")
                        return
                else:
                    self.console.print(f"[yellow]Unknown dataset type: {dataset_type}. Cancelling benchmark.[/]")
                    return
            
            # Run the benchmark
            results = runner.run_with_dataset(dataset)
            
            # Automatically save results first - this adds benchmark_id to the results
            save_path = self._save_api_benchmark_results(results)
            
            # Send email notification if configured
            try:
                from cli.notification import EmailNotificationService
                notification_service = EmailNotificationService(console=self.console)
                
                if notification_service.is_configured() and results.get('benchmark_id'):
                    notification_sent = notification_service.send_benchmark_complete_notification(
                        benchmark_id=results['benchmark_id'],
                        results=results,
                        benchmark_type="Static Red Teaming"
                    )
                    
                    if notification_sent:
                        self.console.print("[dim]Email notification sent for benchmark completion.[/]")
            except Exception as e:
                self.console.print(f"[yellow]Failed to send notification: {str(e)}[/]")
            
            # Display results
            self._display_api_benchmark_results(results)
            
        except Exception as e:
            self.console.print(f"[bold red]Error running benchmark: {str(e)}[/]")
            import traceback
            traceback.print_exc()
    
    def _verify_all_api_keys(self):
        """Verify all possible API keys and inform the user of missing ones.
        This doesn't prompt for keys yet, just informs the user which ones are missing.
        """
        self.console.print("[cyan]Checking API keys availability...[/]")
        
        # Check for common API keys using the centralized API key manager
        missing_keys = []
        
        # Define the key mapping with human-readable names
        key_mappings = {
            "OpenAI": "OPENAI_API_KEY",
            "Google Gemini": "GOOGLE_API_KEY", 
            "HuggingFace": "HF_API_TOKEN",
            "Anthropic": "ANTHROPIC_API_KEY"
        }
        
        for provider_name, key_name in key_mappings.items():
            # Use the centralized API key manager to check for keys
            if self.api_key_manager:
                api_key = self.api_key_manager.get_key(key_name)
            else:
                # Legacy fallback: check environment directly
                api_key = os.environ.get(key_name)
                
            if not api_key:
                missing_keys.append((provider_name, key_name))
        
        # If any keys are missing, inform the user
        if missing_keys:
            self.console.print("[yellow]The following API keys were not found in your configuration:[/]")
            for provider, key_name in missing_keys:
                self.console.print(f"  - [bold]{provider}[/]: {key_name}")
            
            self.console.print("[cyan]Note: You can configure API keys in Settings > API Keys[/]")
            self.console.print("[cyan]You will only be prompted for keys required by your selected models.[/]")
        else:
            self.console.print("[green]✓ All common API keys are available[/]")
    
    def _verify_api_keys_for_models(self, models: List[str]) -> bool:
        """Verify that required API keys are available for the selected models.
        
        Args:
            models: List of model IDs to check
            
        Returns:
            bool: True if all required keys are available, False otherwise
        """
        required_keys = {
            "openai": "OPENAI_API_KEY",
            "gemini": "GOOGLE_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }
        
        missing_keys = {}
        
        for model_id in models:
            # Skip custom models, Ollama models, and HuggingFace models
            if model_id.startswith(("custom:", "ollama:", "hf:", "api:")):
                continue
                
            # Check OpenAI models
            if "gpt" in model_id.lower():
                key = required_keys["openai"]
                # Use centralized API key manager
                if self.api_key_manager:
                    api_key = self.api_key_manager.get_key(key)
                else:
                    api_key = os.environ.get(key)
                    
                if not api_key:
                    missing_keys["OpenAI"] = key
            
            # Check Gemini models
            elif "gemini" in model_id.lower():
                key = required_keys["gemini"]
                # Use centralized API key manager
                if self.api_key_manager:
                    api_key = self.api_key_manager.get_key(key)
                else:
                    api_key = os.environ.get(key)
                    
                if not api_key:
                    missing_keys["Google"] = key
            
            # Check Anthropic models
            elif "claude" in model_id.lower():
                key = required_keys["anthropic"]
                # Use centralized API key manager
                if self.api_key_manager:
                    api_key = self.api_key_manager.get_key(key)
                else:
                    api_key = os.environ.get(key)
                    
                if not api_key:
                    missing_keys["Anthropic"] = key
        
        if missing_keys:
            self.console.print("\n[yellow]The following API keys were not found in your configuration:[/]")
            for provider, key in missing_keys.items():
                self.console.print(f"  - {provider}: {key}")
            
            self.console.print("[cyan]You can configure these API keys in Settings > API Keys[/]")
            self.console.print("[yellow]Or provide them now for this session only:[/]")
            
            # Ask if user wants to provide keys for this session
            provide_keys = inquirer.confirm(
                message="Do you want to provide these keys now for this session?",
                default=True
            )
            
            if provide_keys:
                # Ask for each missing key
                for provider, key in missing_keys.items():
                    value = inquirer.password(
                        message=f"Enter {provider} API key ({key}) - session only"
                    )
                    if value:
                        # Set environment variable for this session
                        os.environ[key] = value
                        self.console.print(f"[green]✓ {provider} API key set for this session[/]")
                    else:
                        self.console.print(f"[yellow]Warning: No key provided for {provider}[/]")
                        return False
            else:
                return False
        
        return True
    
    def _prepare_model_configs(self, models: List[str], model_loader=None, max_tokens: int = 1000, temperature: float = 0.7) -> List[Dict[str, Any]]:
        """Prepare model configurations based on the selected models.
        
        Args:
            models: List of model IDs to configure
            model_loader: Optional ModelLoader instance
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            
        Returns:
            List of model configuration dictionaries
        """
        configs = []
        
        for model_id in models:
            # Handle model prefixes to determine model type
            if model_id.startswith("guardrail:"):
                # Guardrail model
                guardrail_name = model_id[10:]  # Remove the \'guardrail:\' prefix
                configs.append({
                    "type": "guardrail",
                    "model_id": guardrail_name,
                    "name": guardrail_name,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                })
            elif model_id.startswith("hf:"):
                # HuggingFace model
                hf_model_id = model_id[3:]  # Remove the 'hf:' prefix
                configs.append({
                    "type": "huggingface",
                    "model_id": hf_model_id,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                })
            elif model_id.startswith("custom:"):
                # Custom model handler
                handler_name = model_id[7:]  # Remove the 'custom:' prefix
                if model_loader:
                    # Try to get the handler to verify it exists
                    try:
                        handler = model_loader.load_handler(handler_name)
                        if handler:
                            configs.append({
                                "type": "custom",
                                "model_id": handler_name,
                                "custom_name": handler_name,
                                "max_tokens": max_tokens,
                                "temperature": temperature
                            })
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not load custom handler '{handler_name}': {str(e)}[/]")
                else:
                    # Add without verification
                    configs.append({
                        "type": "custom",
                        "model_id": handler_name,
                        "custom_name": handler_name,
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    })
            elif model_id.startswith("ollama:"):
                # Ollama model
                ollama_model_id = model_id[7:]  # Remove the 'ollama:' prefix
                
                # Check if base_url is included as a suffix with '@'
                # Example: ollama:llama2@http://localhost:11434
                if "@" in ollama_model_id:
                    model_name, base_url = ollama_model_id.split("@", 1)
                else:
                    model_name = ollama_model_id
                    base_url = "http://localhost:11434"
                    
                # Add the Ollama model config    
                configs.append({
                    "type": "ollama",
                    "model_id": model_name,
                    "base_url": base_url,
                    "custom_name": f"Ollama: {model_name}",
                    "max_tokens": max_tokens,
                    "temperature": temperature
                })
            elif model_id.startswith("api:"):
                # Custom API model
                api_model_id = model_id[4:]  # Remove the 'api:' prefix
                
                # This requires more complex handling from the UI
                # For now, just add a placeholder config
                configs.append({
                    "type": "custom-api",
                    "model_id": api_model_id,
                    "custom_name": f"API: {api_model_id}",
                    "max_tokens": max_tokens,
                    "temperature": temperature
                })
            elif "gemini" in model_id.lower():
                # Gemini model
                configs.append({
                    "type": "gemini",
                    "model_id": model_id,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                })
            elif "claude" in model_id.lower():
                # Anthropic Claude model
                configs.append({
                    "type": "anthropic",
                    "model_id": model_id,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                })
            else:
                # Default to OpenAI
                configs.append({
                    "type": "openai",
                    "model_id": model_id,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                })
                
        return configs
    
    def _verify_api_environment(self) -> bool:
        """
        Verify that necessary API keys are available from the centralized configuration
        and report status to the user
        
        Returns:
            True if verification passed, False otherwise
        """
        self.console.print("[bold cyan]Verifying API environment...[/]")
        
        missing_keys = []
        
        # Check OpenAI API key
        if self.api_key_manager:
            openai_key = self.api_key_manager.get_key("OPENAI_API_KEY")
        else:
            openai_key = os.environ.get("OPENAI_API_KEY")
            
        if openai_key:
            self.console.print("[green]✓ OPENAI_API_KEY found in configuration[/]")
        else:
            missing_keys.append("OPENAI_API_KEY")
            self.console.print("[yellow]⚠ OPENAI_API_KEY not found in configuration[/]")
        
        # Check Google API key
        if self.api_key_manager:
            google_key = self.api_key_manager.get_key("GOOGLE_API_KEY")
        else:
            google_key = os.environ.get("GOOGLE_API_KEY")
            
        if google_key:
            self.console.print("[green]✓ GOOGLE_API_KEY found in configuration[/]")
        else:
            missing_keys.append("GOOGLE_API_KEY")
            self.console.print("[yellow]⚠ GOOGLE_API_KEY not found in configuration[/]")
        
        # Check Anthropic API key (if needed)
        if self.api_key_manager:
            anthropic_key = self.api_key_manager.get_key("ANTHROPIC_API_KEY")
        else:
            anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
            
        if anthropic_key:
            self.console.print("[green]✓ ANTHROPIC_API_KEY found in configuration[/]")
        else:
            self.console.print("[dim]ℹ ANTHROPIC_API_KEY not found (optional)[/]")
        
        # If any required keys are missing, show instructions
        if missing_keys:
            self.console.print("\n[yellow]Missing required API keys. Please configure them:[/]")
            self.console.print("[cyan]  • Go to Settings > API Keys to configure them[/]")
            self.console.print("[cyan]  • Or set them as environment variables[/]")
            for key in missing_keys:
                self.console.print(f"    • {key}")
            
            # Ask if user wants to continue anyway
            if inquirer.confirm("Continue without all API keys?", default=False):
                self.console.print("[yellow]Continuing with limited functionality...[/]")
                return True
            return False
            
        return True
    
    def _verify_model_availability(self, config: Dict[str, Any]) -> bool:
        """
        Verify that the models specified in the config are available.
        Shows a clear warning if models are not available.
        
        Args:
            config: The benchmark configuration
            
        Returns:
            True if all required models are available, False otherwise
        """
        self.console.print("[bold cyan]Verifying model availability...[/]")
        
        # Check OpenAI models
        openai_model = config.get('model_openai')
        if openai_model:
            try:
                import openai
                # Lightweight model check - just validate the model name without a full API call
                valid_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
                valid_prefixes = ["gpt-3.5-turbo-", "gpt-4-", "gpt-4o-"]
                
                is_valid = openai_model in valid_models or any(openai_model.startswith(prefix) for prefix in valid_prefixes)
                if not is_valid:
                    self.console.print(f"[yellow]Warning: OpenAI model '{openai_model}' may not be valid[/]")
                else:
                    self.console.print(f"[green]✓ OpenAI model '{openai_model}' appears valid[/]")
                    
            except ImportError:
                self.console.print("[yellow]Warning: OpenAI package not installed or API key not set[/]")
        
        # Check Google/Gemini models
        gemini_model = config.get('model_gemini')
        if gemini_model:
            try:
                import google.generativeai as genai
                valid_models = ["gemini-pro", "gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
                
                is_valid = gemini_model in valid_models or gemini_model.startswith("gemini-")
                if not is_valid:
                    self.console.print(f"[yellow]Warning: Gemini model '{gemini_model}' may not be valid[/]")
                else:
                    self.console.print(f"[green]✓ Gemini model '{gemini_model}' appears valid[/]")
                    
            except ImportError:
                self.console.print("[yellow]Warning: Google Generative AI package not installed or API key not set[/]")
        
        # Brief pause to let the user read the verification results
        import time
        time.sleep(1)
        
        return True  # Continue despite warnings
    
    def _get_available_model(self, provider: str, requested_model: Optional[str]) -> str:
        """
        Get an available model for the specified provider, with fallbacks.
        
        Args:
            provider: The model provider ('openai', 'gemini', 'anthropic')
            requested_model: The requested model name
            
        Returns:
            A model name that should be available
        """
        # Default fallback models by provider
        fallbacks = {
            'openai': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o'],
            'gemini': ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash'],
            'anthropic': ['claude-instant-1', 'claude-2', 'claude-3-haiku'],
        }
        
        # If a specific model was requested, use it first
        if requested_model:
            return requested_model
            
        # Otherwise use the first available fallback model
        return fallbacks.get(provider, ['unknown'])[0]
    
    def _filter_available_models(self, model_list: List[str]) -> List[str]:
        """
        Filter a list of models to only include those that are likely available.
        
        Args:
            model_list: List of model names
            
        Returns:
            Filtered list of available models
        """
        if not model_list:
            return []
            
        # Simple check for known model prefixes
        valid_models = []
        for model in model_list:
            if any(model.startswith(prefix) for prefix in ['gpt-', 'gemini-', 'claude-', 'llama-', 'mistral-']):
                valid_models.append(model)
            else:
                self.console.print(f"[yellow]Warning: Unknown model format '{model}', skipping[/]")
                
        return valid_models

    def _run_api_benchmark_on_kubernetes(self, config: Optional[Dict[str, Any]] = None, dataset: Optional[Dict[str, Any]] = None):
        """Run an API benchmark on Kubernetes with the provided configuration and dataset."""
        try:
            # Check if this is an external dataset or internal dataset benchmark
            is_external_dataset = dataset is not None
            
            # Get configuration if not provided
            if not config:
                if is_external_dataset:
                    config = self.ui.get_external_dataset_config()
                else:
                    config = self.ui.get_internal_dataset_config()
                    
            if not config:
                return
                
            # Print info
            self.console.print("[bold cyan]Starting Kubernetes Benchmark Job[/]")
            
            # Create session ID
            session_id = str(uuid.uuid4())
            
            # Different handling based on whether we're using an external dataset or not
            if is_external_dataset:
                try:
                    # Create a backup session
                    # Create session first, then save state
                    self.backup_manager.create_session()
                    self.backup_manager.save_session_state(
                        session_id=session_id,
                        state={
                            "session_id": session_id,
                            "stage": "kubernetes_starting",
                            "dataset_id": dataset.get("id"),
                            "dataset_name": dataset.get("name"),
                            "config": config
                        }
                    )
                    
                    # Load dataset content
                    try:
                        dataset_data = self._load_dataset_content(dataset)
                    except Exception as e:
                        self.console.print(f"[bold red]Error loading dataset: {str(e)}")
                        return
                
                    # Create temporary file to store dataset
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp:
                        # Save dataset to temp file
                        for item in dataset_data:
                            tmp.write(json.dumps(item) + '\n')
                        dataset_path = tmp.name
                    
                    # Initialize the Kubernetes runner
                    from benchmark.runners import KubernetesBenchmarkRunner
                    
                    # Update session status
                    self.backup_manager.save_session_state(session_id, {"stage": "kubernetes_running"})
                    
                    # Create and run the benchmark
                    runner = KubernetesBenchmarkRunner(
                        session_id=session_id,
                        concurrency=config.get("concurrency", 3),
                        models=config.get("models", []),
                        dataset_path=dataset_path,
                        max_tokens=config.get("max_tokens", 4096),
                        temperature=config.get("temperature", 0),
                        console=self.console,
                        backup_manager=self.backup_manager
                    )
                    
                    # Run the benchmark
                    job_id = runner.submit_job()
                    
                    # Display job information
                    if job_id:
                        self.console.print(f"[green]Kubernetes job submitted with ID: {job_id}[/]")
                        self.console.print("[cyan]You can check job status with:[/]")
                        self.console.print(f"[dim]kubectl get job {job_id}[/]")
                        self.console.print(f"[dim]kubectl logs -l job-name={job_id}[/]")
                        
                        # Start monitoring job
                        runner.monitor_job(job_id)
                    else:
                        self.console.print("[red]Failed to submit Kubernetes job.[/]")
                    
                except Exception as k8s_error:
                    self.console.print(f"[bold red]Error in Kubernetes benchmark: {str(k8s_error)}[/]")
                    # Update session status to error
                    self.backup_manager.save_session_state(session_id, {"stage": "kubernetes_error", "error": str(k8s_error)})
                    raise
            else:
                # Internal dataset benchmark
                try:
                    # Create a backup session
                    # Create session first, then save state
                    self.backup_manager.create_session()
                    self.backup_manager.save_session_state(
                        session_id=session_id,
                        state={
                            "session_id": session_id,
                            "stage": "kubernetes_starting",
                            "config": config
                        }
                    )
                    
                    # Initialize the Kubernetes runner
                    from benchmark.runners import KubernetesBenchmarkRunner
                    
                    # Update session status
                    self.backup_manager.save_session_state(session_id, {"stage": "kubernetes_running"})
                    
                    # Create and run the benchmark
                    runner = KubernetesBenchmarkRunner(
                        session_id=session_id,
                        concurrency=config.get("concurrency", 3),
                        dataset_type=config.get("dataset_type"),
                        models=config.get("models", []),
                        max_tokens=config.get("max_tokens", 4096),
                        temperature=config.get("temperature", 0),
                        console=self.console,
                        backup_manager=self.backup_manager
                    )
                    
                    # Run the benchmark
                    job_id = runner.submit_job()
                    
                    # Display job information
                    if job_id:
                        self.console.print(f"[green]Kubernetes job submitted with ID: {job_id}[/]")
                        self.console.print("[cyan]You can check job status with:[/]")
                        self.console.print(f"[dim]kubectl get job {job_id}[/]")
                        self.console.print(f"[dim]kubectl logs -l job-name={job_id}[/]")
                        
                        # Start monitoring job
                        runner.monitor_job(job_id)
                    else:
                        self.console.print("[red]Failed to submit Kubernetes job.[/]")
                    
                except Exception as k8s_error:
                    self.console.print(f"[bold red]Error in Kubernetes benchmark: {str(k8s_error)}[/]")
                    # Update session status to error
                    self.backup_manager.save_session_state(session_id, {"stage": "kubernetes_error", "error": str(k8s_error)})
                    raise
                
        except Exception as e:
            self.console.print(f"[bold red]Error in Kubernetes benchmark: {str(e)}[/]")
            import traceback
            traceback.print_exc()
    
    def _run_flexible_benchmark(self, dataset: Optional[Dict[str, Any]] = None):
        """Run the flexible benchmark for multiple domains"""
        try:
            # Get benchmark configuration
            config = self.ui.get_flexible_benchmark_config()
            if not config:
                return
            
            # If dataset was provided, use it
            if dataset:
                config['dataset'] = dataset
                self.console.print(f"[cyan]Using provided dataset: {dataset.get('name')}[/]")
                
            # Check if user wants to run on Kubernetes
            use_kubernetes = config.pop("use_kubernetes", False)
            
            if use_kubernetes:
                self._run_flexible_benchmark_on_kubernetes(config, dataset)
            else:
                # Original implementation
                from .runners import FlexibleBenchmarkRunner
                
                self.console.print(f"[bold]Running flexible benchmark on domain: {config['domain']}[/]")
                
                # Create output directory
                output_dir = self.benchmark_dir / "outputs" / f"flexible_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.makedirs(output_dir, exist_ok=True)
                
                # Initialize the runner
                runner = FlexibleBenchmarkRunner(
                    db=self.db,
                    console=self.console,
                    backup_manager=self.backup_manager,
                    target_model=config["target_model"],
                    domain=config["domain"],
                    benchmark_name=config.get("benchmark_name"),
                    eval_models=config.get("eval_models"),
                    output_dir=str(output_dir),
                    max_examples=config.get("max_examples", 10),
                    verbose=self.config.get("verbose", False),
                    dataset=dataset if dataset else None  # Pass the dataset if provided
                )
                
                # Run the benchmark
                results = runner.run()
                
                # Save results to database
                try:
                    # Create a results structure for database storage
                    benchmark_results = {
                        "benchmark_id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "benchmark_type": "flexible",
                        "domain": config.get("domain", "unknown"),
                        "target_model": config.get("target_model", "unknown"),
                        "dataset": {
                            "name": dataset.get("name") if dataset else "Generated",
                            "type": "flexible_benchmark"
                        },
                        "results": results,
                        "execution_time": results.get("execution_time", 0),
                        "summary": {
                            "overall_score": results.get("overall_score", 0.0),
                            "passed": results.get("passed", False),
                            "domain": config.get("domain", "unknown"),
                            "target_model": config.get("target_model", "unknown")
                        }
                    }
                    
                    # Save to database using the existing method
                    save_success = self._save_api_benchmark_results(
                        benchmark_results, 
                        dataset_name=f"Flexible Benchmark - {config.get('domain', 'unknown')}"
                    )
                    
                    if save_success:
                        self.console.print("[green]✓ Flexible benchmark results saved to database[/]")
                    else:
                        self.console.print("[yellow]Warning: Could not save flexible benchmark results to database[/]")
                        
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not save flexible benchmark results to database: {str(e)}[/]")
                    import traceback
                    traceback.print_exc()
                
                # Display results
                self._display_flexible_benchmark_results(results)
            
        except Exception as e:
            self.console.print(f"[bold red]Error in flexible benchmark: {str(e)}")
            import traceback
            if config and config.get('verbose', False):
                self.console.print(traceback.format_exc())
    
    def _run_flexible_benchmark_on_kubernetes(self, config: Dict[str, Any], dataset: Optional[Dict[str, Any]] = None):
        """Run flexible benchmark on Kubernetes"""
        try:
            # If dataset is in config (from _run_flexible_benchmark), use it
            dataset = config.pop('dataset', dataset)
            
            # Check if Kubernetes is available
            try:
                from kubernetes import client, config as k8s_config
                k8s_config.load_kube_config()
            except Exception as e:
                self.console.print(f"[bold red]Error: Kubernetes not available: {str(e)}[/]")
                self.console.print("[yellow]Falling back to local benchmark execution.[/]")
                self._run_flexible_benchmark(dataset=dataset)
                return
                
            # Create a unique run ID and output directory
            run_id = f"flex_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            output_dir = str(self.benchmark_dir / "outputs" / run_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Add dataset info to config if available
            if dataset:
                config["dataset_id"] = dataset.get("id")
                config["dataset_name"] = dataset.get("name")
            
            # Save config to output directory
            with open(os.path.join(output_dir, "config.json"), "w") as f:
                json.dump(config, f, indent=2)
                
            # Add benchmark type to config
            config["benchmark_type"] = "flexible"
                
            # Run on Kubernetes
            try:
                self.k8s_manager.run_on_kubernetes(
                    config=config,
                    output_dir=output_dir,
                    run_id=run_id
                )
                
                self.console.print(f"[green]✓ Flexible benchmark started on Kubernetes[/]")
                self.console.print(f"[green]✓ Results will be available in {output_dir}[/]")
                
            except Exception as e:
                self.console.print(f"[bold red]Error running on Kubernetes: {str(e)}[/]")
                self.console.print("[yellow]Falling back to local benchmark execution.[/]")
                # Run locally by restoring the original config and calling the method
                self._run_flexible_benchmark(dataset=dataset)
                
        except Exception as e:
            self.console.print(f"[bold red]Error: {str(e)}[/]")
            traceback.print_exc()
    
    def _resume_kubernetes_benchmark(self, session: Dict[str, Any]):
        """Resume a Kubernetes benchmark from a saved session"""
        try:
            self.console.print(f"[bold cyan]Resuming Kubernetes benchmark session: {session.get('session_id')}[/]")
            
            # Initialize the Kubernetes runner
            from benchmark.runners import KubernetesBenchmarkRunner
            
            # Create the runner with session data
            runner = KubernetesBenchmarkRunner(
                session_id=session.get('session_id'),
                console=self.console,
                backup_manager=self.backup_manager
            )
            
            # Get job ID from session
            job_id = session.get('job_id')
            if not job_id:
                self.console.print("[yellow]No job ID found in session. Cannot resume.[/]")
                return
            
            # Resume monitoring
            runner.monitor_job(job_id)
        except Exception as e:
            self.console.print(f"[bold red]Error resuming Kubernetes benchmark: {str(e)}[/]")
            import traceback
            traceback.print_exc()
                    
    def _display_flexible_benchmark_results(self, results: Dict[str, Any]):
        """Display formatted results from flexible benchmark"""
        from rich.panel import Panel
        from rich.table import Table
        
        # Check if results contain error
        if 'error' in results:
            self.console.print(f"[bold red]Benchmark failed with error: {results['error']}[/]")
            return
            
        # Create a summary panel
        domain = results.get('domain', 'unknown')
        model = results.get('target_model', 'unknown')
        score = results.get('overall_score', 0.0)
        passed = results.get('passed', False)
        
        status = "[bold green]PASSED" if passed else "[bold red]FAILED"
        
        summary = f"""{model} Benchmark Results for {domain.capitalize()} Domain
        
Overall Score: [bold]{score:.2f}[/bold] / 1.0
Status: {status}[/]
        """
        
        self.console.print(Panel(summary, title="[bold]Benchmark Summary[/]", border_style="green" if passed else "red"))
        
        # Display metrics
        if 'metrics' in results and results['metrics']:
            metrics_table = Table(title="Detailed Metrics")
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Score", style="green")
            
            for metric, value in results['metrics'].items():
                if isinstance(value, (int, float)):
                    metrics_table.add_row(metric.capitalize(), f"{value:.2f}")
            
            self.console.print(metrics_table)
        
        # Display evaluator models used
        if 'eval_models' in results and results['eval_models']:
            self.console.print("\n[bold]Evaluator Models Used:[/]")
            for eval_model in results['eval_models']:
                provider = eval_model.get('provider', 'unknown')
                model_name = eval_model.get('model', 'unknown')
                self.console.print(f"- {provider.capitalize()}: {model_name}")
        
        # Results location
        if 'results_path' in results:
            self.console.print(f"\n[dim]Full results saved to: {results['results_path']}[/]")

    def _run_performance_benchmark(self, benchmark_type: str, dataset: Optional[Dict[str, Any]] = None):
        """Run performance benchmarks"""
        self.console.print(f"[yellow]Performance benchmarking is not yet implemented: {benchmark_type}[/]")
        if dataset:
            self.console.print(f"[yellow]Note: A dataset was provided ({dataset.get('name')}), but it will not be used until the feature is implemented.[/]")
    
    def list_benchmark_results(self):
        """List all benchmark results from the database with improved handling for large benchmarks"""
        all_results = self.results_viewer.list_all_results(include_large_benchmarks=True)
        
        # If we have results, offer to show large benchmarks specifically
        if all_results and any(r['total_prompts'] >= 100 for r in all_results):
            if inquirer.confirm("Would you like to view your large benchmark results specifically?", default=True):
                large_benchmark = self.results_viewer.find_large_benchmark(min_prompts=100)
                if large_benchmark:
                    self.results_viewer.display_api_results(large_benchmark)
        
    def view_benchmark_results(self):
        """View and analyze detailed benchmark results"""
        # Check if there are any Kubernetes benchmarks running
        k8s_sessions = [s for s in self.backup_manager.list_sessions() if s.get("stage") == "kubernetes_running"]
        
        if k8s_sessions and inquirer.confirm(
            message="There are Kubernetes benchmarks running. Would you like to view their status?",
            default=True
        ):
            session = self.ui.select_session(k8s_sessions)
            if session:
                self._resume_kubernetes_benchmark(session)
                return
                
        # If no Kubernetes benchmarks or user doesn't want to view them, show regular results
        self.results_viewer.view_results()
    
    def export_benchmark_data(self):
        """Export benchmark data for reports"""
        self.results_viewer.export_results()
        
    def show_benchmark_statistics(self):
        """Show statistics across all benchmarks"""
        self.results_viewer.show_statistics()
    
    def fix_benchmark_results(self):
        """Fix benchmark result locations and permissions"""
        self.console.print("[bold blue]Checking and fixing benchmark results...[/]")
        
        try:
            # Import the diagnostic and fix utility
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            from utils.benchmark_storage_fix import BenchmarkStorageFix
            
            # Initialize and run the fixer
            fixer = BenchmarkStorageFix()
            fixer.run_diagnostics()
            fixer.fix_issues()
            
            # Test if the fixes worked by checking for results now
            self.console.print("\n[bold yellow]Checking if benchmark results are now visible...[/]")
            results = self.results_viewer.list_all_results(limit=5)
            
            if results:
                self.console.print(f"[bold green]Success! Found {len(results)} benchmark results.[/]")
                self.console.print("You can now view results using the 'View results' option.")
            else:
                self.console.print("[bold red]Still no benchmark results found.[/]")
                self.console.print("Try running a new benchmark test to see if results are saved correctly.")
            
        except ImportError:
            self.console.print("[yellow]Benchmark storage fix utility not found.[/]")
            self.console.print("Creating benchmark_results directory with proper permissions...")
            
            # Basic fallback fix
            try:
                results_dir = Path("/home/ubuntu/revert/dravik/benchmark_results")
                results_dir.mkdir(exist_ok=True, parents=True)
                os.chmod(str(results_dir), 0o755)  # rwxr-xr-x
                self.console.print(f"[green]Created {results_dir} with proper permissions[/]")
                
                # Try creating a simple test file
                test_file = results_dir / "test_write.tmp"
                with open(test_file, 'w') as f:
                    f.write(f"Write test: {datetime.now().isoformat()}")
                if test_file.exists():
                    test_file.unlink()  # Clean up
                    self.console.print("[green]Successfully tested write permissions[/]")
            except Exception as e:
                self.console.print(f"[red]Error during basic fix: {e}[/]")
                
        except Exception as e:
            self.console.print(f"[bold red]Error fixing benchmark results: {e}[/]")
            import traceback
            traceback.print_exc()

    def _display_api_benchmark_results(self, results):
        """Display API benchmark results in a nice format."""
        try:
            # Check if results are valid
            if not results or not isinstance(results, dict):
                self.console.print("[yellow]No valid results to display[/]")
                return
            
            # Ensure we have metrics
            if "metrics" not in results:
                results["metrics"] = {}
            
            # Create metrics if missing
            if "overall_bypass_rate" not in results["metrics"]:
                # Calculate overall bypass rate if missing
                bypass_count = sum(1 for example in results.get("examples", []) 
                                  if any(r.get("bypassed", False) for r in example.get("responses", [])))
                example_count = len(results.get("examples", []))
                if example_count > 0:
                    results["metrics"]["overall_bypass_rate"] = f"{(bypass_count / example_count) * 100:.2f}%"
                else:
                    results["metrics"]["overall_bypass_rate"] = "0.00%"
            
            # Extract timestamp
            timestamp = results.get("timestamp", "Unknown")
            if isinstance(timestamp, str) and "T" in timestamp:
                # Convert ISO format to readable format
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            # Get execution time
            execution_time = results.get("execution_time", 0)
            
            # Get examples count
            examples_count = len(results.get("examples", []))
            
            # Calculate overall bypass rate
            bypass_rate = results["metrics"].get("overall_bypass_rate", "0.00%")
            if not isinstance(bypass_rate, str):
                bypass_rate = f"{bypass_rate * 100:.2f}%"
            
            # Calculate success/fail ratio
            success_count = sum(1 for example in results.get("examples", []) 
                              if any(r.get("success", False) for r in example.get("responses", [])))
            fail_count = examples_count - success_count
            success_fail = f"{success_count}/{fail_count}"
            
            # Display summary
            self.console.print("\n[bold]Benchmark Results[/]")
            self.console.print(f"Timestamp: [cyan]{timestamp}[/]")
            self.console.print(f"Total execution time: [cyan]{execution_time:.2f}[/] seconds")
            self.console.print(f"Examples tested: [cyan]{examples_count}[/]")
            self.console.print(f"Overall Bypass Rate: [cyan]{bypass_rate}[/]")
            self.console.print(f"Total Success/Fail: [cyan]{success_fail}[/]")
            
            # Model performance summary
            self.console.print("\n[bold]Model Performance Summary[/]")
            
            # Create a table for model performance
            table = Table(show_header=True, header_style="bold")
            table.add_column("Model", style="dim")
            table.add_column("Bypass Rate", style="cyan")
            table.add_column("Avg Response Time", style="cyan")
            table.add_column("Success/Total", style="cyan")
            
            # Process each model's results
            models_data = {}
            
            # Extract model results from examples
            for example in results.get("examples", []):
                for response in example.get("responses", []):
                    model_name = response.get("model", "Unknown")
                    if model_name not in models_data:
                        models_data[model_name] = {
                            "total": 0,
                            "bypassed": 0,
                            "success": 0,
                            "response_time": 0,
                            "total_time": 0
                        }
                    
                    models_data[model_name]["total"] += 1
                    
                    if response.get("bypassed", False):
                        models_data[model_name]["bypassed"] += 1
                    
                    if response.get("success", False):
                        models_data[model_name]["success"] += 1
                    
                    # Add response time if available
                    if "response_time" in response:
                        models_data[model_name]["total_time"] += response["response_time"]
                        models_data[model_name]["response_time"] += 1
            
            # If no model data was extracted, try to get from the results models list
            if not models_data and "models" in results:
                for model_info in results.get("models", []):
                    model_name = model_info.get("name", str(model_info))
                    models_data[model_name] = {
                        "total": examples_count,
                        "bypassed": 0,
                        "success": examples_count,  # Assume all successful unless we have detailed data
                        "response_time": 0,
                        "total_time": 0
                    }
            
            # If still no model data, try to extract from models_tested field
            if not models_data and "models_tested" in results:
                for model in results.get("models_tested", []):
                    if isinstance(model, dict):
                        # Handle complex model objects with examples
                        model_name = model.get("name", "unknown")
                        if not model_name or model_name == "unknown":
                            # Try to construct name from provider info
                            provider = model.get("provider", "unknown")
                            model_id = model.get("model_id", "unknown")
                            model_name = f"{provider} ({model_id})"
                        
                        # Extract examples data
                        examples = model.get("examples", [])
                        total_examples = len(examples)
                        
                        if total_examples > 0:
                            success_count = sum(1 for ex in examples if ex.get("success", False))
                            bypassed_count = sum(1 for ex in examples if ex.get("evaluation") == "BYPASS")
                            total_time = sum(ex.get("response_time", 0) for ex in examples)
                            
                            models_data[model_name] = {
                                "total": total_examples,
                                "bypassed": bypassed_count,
                                "success": success_count,
                                "response_time": total_examples,  # Count for averaging
                                "total_time": total_time
                            }
                    else:
                        # Handle simple string model names
                        model_name = model if isinstance(model, str) else str(model)
                        models_data[model_name] = {
                            "total": examples_count,
                            "bypassed": 0,
                            "success": examples_count,
                            "response_time": 0,
                            "total_time": 0
                        }
            
            # Add rows to the table
            for model_name, data in models_data.items():
                # Calculate metrics
                total = data["total"]
                bypassed = data["bypassed"]
                success = data["success"]
                
                # Bypass rate
                bypass_pct = (bypassed / total) * 100 if total > 0 else 0
                bypass_rate_str = f"{bypass_pct:.2f}%"
                
                # Average response time
                avg_time = data["total_time"] / data["response_time"] if data["response_time"] > 0 else 0
                avg_time_str = f"{avg_time:.2f}s"
                
                # Success ratio
                success_ratio = f"{success}/{total}"
                
                # Add to table
                table.add_row(model_name, bypass_rate_str, avg_time_str, success_ratio)

            # Display the table
            self.console.print(table)
            
            # Just display the results without prompting for further action
            self.console.print("\n[green]✓ Benchmark completed successfully[/]")
                
        except Exception as e:
            self.console.print(f"[bold red]Error displaying results: {e}[/]")
            import traceback
            self.console.print(traceback.format_exc())
            self.console.print("[yellow]Showing available data keys:[/]")
            if results:
                self.console.print(", ".join(results.keys()))

    def _view_model_details(self, examples):
        """Display detailed results grouped by model"""
        if not examples:
            self.console.print("[yellow]No examples to display[/]")
            return
            
        # Collect all models
        models = set()
        for example in examples:
            for response in example.get("responses", []):
                models.add(response.get("model", "Unknown"))
        
        # For each model, show results
        for model in sorted(models):
            self.console.print(f"\n[bold]Model: {model}[/]")
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("Prompt ID", style="dim")
            table.add_column("Bypass", style="red")
            table.add_column("Response Preview", style="cyan")
            
            for i, example in enumerate(examples):
                for response in example.get("responses", []):
                    if response.get("model") == model:
                        prompt_id = example.get("id", f"prompt_{i+1}")
                        bypassed = "✓" if response.get("bypassed", False) else "✗"
                        response_text = response.get("response", "")
                        preview = response_text[:50] + "..." if len(response_text) > 50 else response_text
                        
                        table.add_row(prompt_id, bypassed, preview)
            
            self.console.print(table)

    def _save_api_benchmark_results(self, results, dataset_id=None, dataset_name=None):
        """Save API benchmark results to database.
        
        Args:
            results: Benchmark results dictionary
            dataset_id: Optional dataset ID if used
            dataset_name: Optional dataset name if used
            
        Returns:
            Success status as boolean
        """
        try:
            # Generate unique benchmark ID if not present
            if 'benchmark_id' not in results:
                benchmark_id = str(uuid.uuid4())
                results['benchmark_id'] = benchmark_id
            else:
                benchmark_id = results['benchmark_id']
                
            # Add timestamp if not present
            if 'timestamp' not in results:
                results['timestamp'] = datetime.now().isoformat()
            
            # Save to database
            if hasattr(self, 'db') and self.db:
                try:
                    # Get dataset name if available
                    if not dataset_name and 'dataset' in results and isinstance(results['dataset'], dict):
                        dataset_name = results['dataset'].get('name', 'Custom Dataset')
                    
                    # Save directly using db.save_benchmark_result
                    success = self.db.save_benchmark_result(results)
                    
                    if success:
                        self.console.print("[green]✓ Results saved to database[/]")
                    else:
                        self.console.print("[yellow]Warning: Could not save results to database[/]")
                    
                    return success
                    
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not save to database: {str(e)}[/]")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                self.console.print("[red]Error: Database not available. Results cannot be saved.[/]")
                return False
            
        except Exception as e:
            self.console.print(f"[bold red]Error saving results: {str(e)}[/]")
            import traceback
            traceback.print_exc()
            return False

    def _load_dataset_content(self, dataset):
        """Load the content of a dataset based on its ID and type."""
        try:
            dataset_id = dataset.get("id")
            dataset_type = dataset.get("type")
            dataset_name = dataset.get("name")
            
            if not dataset_id and not dataset_name:
                raise ValueError("Dataset ID or name is missing")
            
            self.console.print(f"[cyan]Loading dataset {dataset.get('name', 'Unknown')}...[/]")
            
            # Check if dataset is in file system
            dataset_path = None
            if "path" in dataset and dataset["path"]:
                dataset_path = dataset["path"]
                if os.path.exists(dataset_path):
                    # Load directly from file
                    with open(dataset_path, 'r') as f:
                        if dataset_path.endswith('.json'):
                            data = json.load(f)
                        elif dataset_path.endswith('.jsonl'):
                            data = [json.loads(line) for line in f if line.strip()]
                        else:
                            raise ValueError(f"Unsupported file format: {dataset_path}")
                    
                    # Extract examples if they're nested in the data structure
                    return self._extract_examples_from_dataset(data)
            
            # Handle HuggingFace datasets specifically
            if dataset_type == "huggingface":
                self.console.print(f"[cyan]Loading HuggingFace dataset: {dataset_name}[/]")
                dataset_content = self.db.get_huggingface_dataset(dataset_name)
                
                if not dataset_content:
                    raise ValueError(f"HuggingFace dataset {dataset_name} not found in database")
                
                # Extract examples from dataset content
                return self._extract_examples_from_dataset(dataset_content)
            
            # If not in file system or path not found, try to load from database
            if not dataset_type:
                # Try HuggingFace datasets first if we have a name
                if dataset_name:
                    hf_content = self.db.get_huggingface_dataset(dataset_name)
                    if hf_content:
                        self.console.print(f"[green]Dataset found as HuggingFace dataset[/]")
                        return self._extract_examples_from_dataset(hf_content)
                
                # Try different types if no type is specified
                for possible_type in ["raw", "formatted", "structured", "poc"]:
                    content = self.db.get_dataset_content(possible_type, dataset_id)
                    if content:
                        self.console.print(f"[green]Dataset found with type: {possible_type}[/]")
                        return self._extract_examples_from_dataset(content)
                
                raise ValueError(f"Dataset {dataset_id or dataset_name} not found in any collection")
            
            # Get from database based on dataset type
            if dataset_type in ["raw", "formatted", "structured", "poc"]:
                # Get content directly from database
                self.console.print(f"[cyan]Getting dataset content with type: {dataset_type}, id: {dataset_id}[/]")
                dataset_content = self.db.get_dataset_content(dataset_type, dataset_id)
                
                if not dataset_content:
                    raise ValueError(f"Dataset {dataset_id} not found in database with type {dataset_type}")
                
                # Extract examples from dataset content
                return self._extract_examples_from_dataset(dataset_content)
            else:
                raise ValueError(f"Unsupported dataset type: {dataset_type}")
                
        except Exception as e:
            self.console.print(f"[bold red]Error loading dataset: {str(e)}")
            import traceback
            self.console.print(traceback.format_exc())
            raise

    def _extract_examples_from_dataset(self, dataset):
        """Extract examples from the dataset regardless of structure."""
        try:
            # Case 1: Dataset is already a list of examples
            if isinstance(dataset, list):
                self.console.print(f"[green]Found {len(dataset)} examples in list format[/]")
                return dataset
                
            # Case 2: Dataset is a dictionary with 'examples' field
            if isinstance(dataset, dict) and 'examples' in dataset and isinstance(dataset['examples'], list):
                self.console.print(f"[green]Found {len(dataset['examples'])} examples in 'examples' field[/]")
                return dataset['examples']
                
            # Case 3: Dataset is a dictionary with 'data' field
            if isinstance(dataset, dict) and 'data' in dataset and isinstance(dataset['data'], list):
                self.console.print(f"[green]Found {len(dataset['data'])} examples in 'data' field[/]")
                return dataset['data']
            
            # Case 4: If it's a dictionary but doesn't have examples/data, convert it to a single example
            if isinstance(dataset, dict):
                self.console.print("[yellow]Dataset doesn't contain examples array; treating as single example[/]")
                return [dataset]
                
            # Handle unknown format
            self.console.print("[yellow]Unknown dataset format, returning as is[/]")
            return dataset
            
        except Exception as e:
            self.console.print(f"[yellow]Error extracting examples: {str(e)}. Returning dataset as is.[/]")
            return dataset

    def _export_model_results(self, model_name, metrics):
        """Export detailed results for a specific model"""
        try:
            # Create export dir if it doesn't exist
            export_dir = Path(self.config.get('export_dir', Path.home() / "dravik" / "exports"))
            export_dir.mkdir(exist_ok=True, parents=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            provider, name = model_name.split(':', 1) if ':' in model_name else ("unknown", model_name)
            filename = f"{provider}_{name}_{timestamp}.json"
            export_path = export_dir / filename
            
            # Export data
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2)
                
            self.console.print(f"[green]Exported results to {export_path}[/]")
            
        except Exception as e:
            self.console.print(f"[red]Error exporting results: {str(e)}[/]")
            
    def _export_benchmark_results(self, results):
        """Export all benchmark results to a file"""
        try:
            # Create export dir if it doesn't exist
            export_dir = Path(self.config.get('export_dir', Path.home() / "dravik" / "exports"))
            export_dir.mkdir(exist_ok=True, parents=True)
            
            # Ask for export format
            questions = [
                inquirer.List(
                    'format',
                    message="Select export format",
                    choices=[
                        ('JSON', 'json'),
                        ('CSV', 'csv')
                    ]
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers:
                return
                
            export_format = answers['format']
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.{export_format}"
            export_path = export_dir / filename
            
            # Export data
            if export_format == 'json':
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
            elif export_format == 'csv':
                # Create CSV with summary data
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow(['Model', 'Bypass Rate', 'Success Count', 'Total Prompts', 'Avg Response Time'])
                    
                    # Write overall data
                    writer.writerow([
                        'OVERALL',
                        results.get('bypass_rate_pct', '0.00%'),
                        results.get('success_count', 0),
                        results.get('total_prompts', 0),
                        f"{results.get('avg_response_time', 0):.4f}s"
                    ])
                    
                    # Write per-model data
                    for model_name, metrics in results.get('model_metrics', {}).items():
                        writer.writerow([
                            model_name,
                            metrics.get('bypass_rate_pct', '0.00%'),
                            metrics.get('success_count', 0),
                            metrics.get('total_prompts', 0),
                            f"{metrics.get('avg_response_time', 0):.4f}s"
                        ])
                        
                # Also export detailed results as JSON if requested
                if inquirer.confirm("Export detailed results as JSON?", default=True):
                    detailed_path = export_dir / f"benchmark_details_{timestamp}.json"
                    with open(detailed_path, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2)
                    self.console.print(f"[green]Exported detailed results to {detailed_path}[/]")
                    
            self.console.print(f"[green]Exported results to {export_path}[/]")
            
        except Exception as e:
            self.console.print(f"[red]Error exporting results: {str(e)}[/]")

    def register_custom_model(self):
        """Register a custom model for benchmarking"""
        try:
            # Import the ModelLoader
            from benchmarks.models.model_loader import ModelLoader
            
            # Create a new ModelLoader instance
            model_loader = ModelLoader(verbose=True)
            
            # Show introduction panel
            self.console.print(Panel.fit(
                "[bold]Custom Model Registration[/]\n\n"
                "Register a custom model to use in benchmarks. You can register:\n"
                "• Local Ollama models running on your machine\n"
                "• Custom API endpoints with full control over request format\n"
                "• Any API endpoint with a custom curl command and prompt placeholder\n\n"
                "For the static red teaming tool, you can specify a custom placeholder for where prompts are inserted.",
                title="[cyan]CUSTOM MODEL REGISTRATION[/]",
                border_style="cyan"
            ))
            
            # Ask about model type
            model_type_question = inquirer.list_input(
                "What type of model would you like to register?",
                choices=[
                    ("Local Ollama model (running on your machine)", "ollama"),
                    ("Custom API endpoint (including any API with curl command)", "custom-api"),
                ],
                default="ollama"
            )
            
            # Get model name
            model_name_question = [
                inquirer.Text(
                    'model_name',
                    message="Enter a name for this custom model",
                    validate=lambda _, x: bool(x.strip())
                )
            ]
            
            model_name_answer = inquirer.prompt(model_name_question)
            if not model_name_answer:
                self.console.print("[yellow]Registration cancelled.[/]")
                return
                
            model_name = model_name_answer['model_name']
            
            # Handle Ollama models
            if model_type_question == "ollama":
                # Get Ollama model details
                ollama_config = self._register_ollama_model(model_name)
                if not ollama_config:
                    return
                
                # Register the model
                try:
                    model_loader.register_custom_model(
                        model_name,
                        ollama_config
                    )
                    self.console.print(f"[bold green]✓ Ollama model '{model_name}' registered successfully![/]")
                except Exception as e:
                    self.console.print(f"[bold red]Error registering Ollama model: {str(e)}[/]")
                    
            # Handle custom API models
            else:
                # Get custom API model details
                custom_config = self._register_custom_api_model(model_name)
                if not custom_config:
                    return
                
                # Register the model
                try:
                    model_loader.register_custom_model(
                        model_name,
                        custom_config
                    )
                    self.console.print(f"[bold green]✓ Custom API model '{model_name}' registered successfully![/]")
                except Exception as e:
                    self.console.print(f"[bold red]Error registering custom API model: {str(e)}[/]")
                
            # Show instructions for using the model
            self.console.print("\n[bold]How to use your custom model:[/]")
            self.console.print("• Select 'LLM Red Teaming' from the main menu")
            self.console.print("• Select 'Static Red Teaming' from the LLM Red Teaming menu")
            self.console.print("• Your custom model will appear in the model selection list under 'Custom' models")
            self.console.print("• After selecting the model and completing the benchmark, your results will be available in the 'View Results' menu")
                
        except ImportError as e:
            self.console.print(f"[bold red]Error: Required module not found: {str(e)}[/]")
        except Exception as e:
            self.console.print(f"[bold red]Error: {str(e)}[/]")
            import traceback
            traceback.print_exc()
            
    def _register_ollama_model(self, model_name: str) -> dict:
        """Register an Ollama model
        
        Args:
            model_name: User-specified name for the model
            
        Returns:
            Configuration dictionary or None if cancelled
        """
        self.console.print("\n[bold]Ollama Model Registration[/]")
        self.console.print("This will register a model running in your local Ollama instance.")
        
        # Check if Ollama is running
        import subprocess
        import sys
        import platform
        
        is_windows = platform.system() == "Windows"
        curl_command = "curl" if not is_windows else "curl.exe"
        
        try:
            # Try to get the list of models from Ollama
            with self.console.status("Checking if Ollama is running...", spinner="dots"):
                process = subprocess.run(
                    [curl_command, "-s", "http://localhost:11434/api/tags"], 
                    capture_output=True, 
                    timeout=5,
                    check=False
                )
            
            if process.returncode != 0:
                self.console.print("[bold red]Error: Could not connect to Ollama.[/]")
                self.console.print("[yellow]Please make sure Ollama is running on your machine.[/]")
                self.console.print("[yellow]Visit https://ollama.ai to download and install Ollama.[/]")
                return None
                
            # Parse the response to get available models
            import json
            try:
                response = json.loads(process.stdout)
                models = response.get("models", [])
                if not models:
                    self.console.print("[yellow]No models found in your Ollama instance.[/]")
                    self.console.print("[yellow]Please pull a model first using 'ollama pull <model>' command.[/]")
                    return None
                    
                # Create a list of model names
                model_names = [model["name"] for model in models]
                
                # Show the available models
                self.console.print(f"[green]Found {len(models)} models in your Ollama instance:[/]")
                for i, model_name in enumerate(model_names):
                    self.console.print(f"  {i+1}. [cyan]{model_name}[/]")
                    
            except json.JSONDecodeError:
                self.console.print("[yellow]Could not parse response from Ollama. Proceeding anyway.[/]")
                model_names = []
                
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            self.console.print(f"[bold red]Error checking Ollama: {str(e)}[/]")
            self.console.print("[yellow]Please make sure Ollama is running on your machine.[/]")
            return None
        
        # Ask for Ollama model ID
        ollama_model_question = [
            inquirer.Text(
                'ollama_model_id',
                message="Enter Ollama model name (e.g., 'llama2', 'mistral')",
                validate=lambda _, x: bool(x.strip()),
                default=model_names[0] if model_names else None
            )
        ]
        
        ollama_model_answer = inquirer.prompt(ollama_model_question)
        if not ollama_model_answer:
            self.console.print("[yellow]Registration cancelled.[/]")
            return None
            
        ollama_model_id = ollama_model_answer['ollama_model_id']
        
        # Ask for Ollama API URL
        ollama_url_question = [
            inquirer.Text(
                'ollama_url',
                message="Enter Ollama API URL",
                default="http://localhost:11434"
            )
        ]
        
        ollama_url_answer = inquirer.prompt(ollama_url_question)
        if not ollama_url_answer:
            self.console.print("[yellow]Registration cancelled.[/]")
            return None
            
        ollama_url = ollama_url_answer['ollama_url']
        
        # Create the configuration dictionary
        config = {
            "type": "ollama",
            "model_id": ollama_model_id,
            "base_url": ollama_url
        }
        
        # Show the configuration summary
        self.console.print("\n[bold]Configuration Summary:[/]")
        self.console.print(f"Model Name: [cyan]{model_name}[/]")
        self.console.print(f"Ollama Model: [cyan]{ollama_model_id}[/]")
        self.console.print(f"Ollama API URL: [cyan]{ollama_url}[/]")
        
        # Confirm registration
        if not inquirer.confirm("Register this Ollama model?", default=True):
            self.console.print("[yellow]Registration cancelled.[/]")
            return None
            
        return config
    
    def _register_custom_api_model(self, model_name: str) -> dict:
        """Register a custom API model
        
        Args:
            model_name: User-specified name for the model
            
        Returns:
            Configuration dictionary or None if cancelled
        """
        self.console.print("\n[bold]Custom API Model Registration[/]")
        self.console.print("You can register a model using either a direct API endpoint or a curl command.")
        
        # Ask which approach they want to use
        approach_question = inquirer.list_input(
            "How would you like to access your custom model?",
            choices=[
                ("Use a curl command (recommended for complex APIs)", "curl"),
                ("Configure a direct HTTP endpoint", "http")
            ],
            default="curl"
        )
        
        if approach_question == "curl":
            # Display instructions for curl command format
            self.console.print(Panel(
                "[bold]Curl Command Format Instructions[/]\n\n"
                "1. Enter a valid curl command that invokes your model API\n"
                "2. Include a placeholder like [bold]{prompt}[/] where your prompt should be inserted\n"
                "3. The command should return a JSON response containing the model's output\n\n"
                "[dim]Example: curl --location 'https://api.example.com/generate' --header 'Content-Type: application/json' --data '{ \"prompt\": \"{prompt}\", \"max_tokens\": 1000 }'[/dim]",
                title="[cyan]Curl Command Guide[/]",
                border_style="cyan"
            ))
            
            # Get curl command with enhanced multi-line support
            curl_command = ""
            while not curl_command.strip():
                try:
                    # Use the new multi-line input handler
                    curl_command = self._get_multiline_curl_input(
                        "Enter your API curl command:",
                        context="curl"
                    )
                    
                    if not curl_command.strip():
                        self.console.print("[yellow]Please enter a curl command.[/]")
                        continue
                        
                    # Validate the curl command
                    is_valid, error_msg = self._validate_curl_command(curl_command, "{prompt}")
                    if not is_valid:
                        self.console.print(f"[red]Invalid curl command: {error_msg}[/]")
                        
                        # Ask if they want to try again or continue anyway
                        choice = inquirer.list_input(
                            "What would you like to do?",
                            choices=[
                                "Try entering the curl command again",
                                "Continue anyway (advanced users)",
                                "Cancel registration"
                            ]
                        )
                        
                        if choice == "Try entering the curl command again":
                            curl_command = ""
                            continue
                        elif choice == "Cancel registration":
                            self.console.print("[yellow]Registration cancelled.[/]")
                            return None
                        # else: continue anyway
                        
                except KeyboardInterrupt:
                    self.console.print("[yellow]Registration cancelled.[/]")
                    return None
            
            # Display the cleaned curl command for confirmation
            self.console.print("\n[bold cyan]Curl Command Summary:[/]")
            # Show a more readable version for long commands
            if len(curl_command) > 100:
                self.console.print("[green]Command successfully parsed and cleaned.[/]")
                self.console.print(f"[dim]Length: {len(curl_command)} characters[/dim]")
                # Show first part and last part
                preview = curl_command[:50] + " ... " + curl_command[-50:]
                self.console.print(f"[green]{preview}[/]")
"""Main benchmark command implementation"""
from rich.console import Console
from rich.panel import Panel
from typing import Optional, Dict, Any, List, Tuple, Union, Set, Callable
import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import time
import inquirer
import traceback
import uuid
import asyncio
import random
import subprocess
import glob
import logging
import numpy as np
import shutil
import pytz
import asyncio
import json
import re
import csv
import time
import subprocess
import ast
import hashlib
import uuid
import traceback
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.live import Live
from rich.layout import Layout
from rich.columns import Columns
import importlib.util
import pkg_resources
import re

from .runners import APIBenchmarkRunner, KubernetesBenchmarkManager
from .results import ResultsViewer
from .ui import BenchmarkUI
from benchmarks.utils.backup_manager import BackupManager
from system_monitor import setup_system_monitor
from cli.notification.email_service import EmailNotificationService

# Add retry-related imports
import random
from enum import Enum


class RetryableError(Exception):
    """Exception for errors that should be retried"""
    pass


class RateLimitError(RetryableError):
    """Exception for rate limit errors"""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class RetryConfig:
    """Configuration for retry logic"""
    def __init__(self, 
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int, suggested_delay: Optional[float] = None) -> float:
        """Calculate delay for the given attempt number"""
        if suggested_delay:
            # If the API suggests a specific delay (e.g., Retry-After header), use it
            delay = min(suggested_delay, self.max_delay)
        else:
            # Calculate exponential backoff delay
            delay = self.base_delay * (self.exponential_base ** attempt)
            delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable"""
    error_str = str(error).lower()
    
    # Rate limit errors
    rate_limit_indicators = [
        'rate limit', 'rate_limit', 'ratelimit',
        'too many requests', 'quota exceeded',
        'throttled', 'throttling',
        '429', 'status_code=429'
    ]
    
    # Temporary network/server errors
    temporary_error_indicators = [
        'timeout', 'connection', 'network',
        'temporary', 'temporarily',
        '502', '503', '504',
        'bad gateway', 'service unavailable', 'gateway timeout',
        'internal server error', '500'
    ]
    
    # Check for retryable error patterns
    for indicator in rate_limit_indicators + temporary_error_indicators:
        if indicator in error_str:
            return True
    
    return False


def extract_retry_after(error: Exception) -> Optional[float]:
    """Extract retry-after delay from error message or headers"""
    error_str = str(error)
    
    # Look for retry-after patterns in error message
    import re
    
    # Pattern: "retry after X seconds"
    match = re.search(r'retry.*?after.*?(\d+(?:\.\d+)?)', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # Pattern: "wait X seconds"
    match = re.search(r'wait.*?(\d+(?:\.\d+)?)\s*seconds?', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # Pattern: "try again in X minutes"
    match = re.search(r'try.*?again.*?in.*?(\d+(?:\.\d+)?)\s*minutes?', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1)) * 60
    
    return None


async def retry_with_backoff(
    func,
    *args,
    retry_config: RetryConfig = None,
    console: Console = None,
    prompt_info: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute a function with retry logic and exponential backoff
    
    Args:
        func: The function to execute
        *args: Arguments for the function
        retry_config: Configuration for retry behavior
        console: Console for logging
        prompt_info: Information about the prompt being processed
        **kwargs: Keyword arguments for the function
    
    Returns:
        Result dictionary with success/error information
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    if console is None:
        console = Console()
    
    last_error = None
    
    for attempt in range(retry_config.max_retries + 1):
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # If we get here, the function succeeded
            if attempt > 0:
                console.print(f"[green]✓ Retry successful after {attempt} attempt(s)[/]")
            
            return {
                "success": True,
                "result": result,
                "attempts": attempt + 1
            }
            
        except Exception as e:
            last_error = e
            
            # Check if this is the last attempt
            if attempt >= retry_config.max_retries:
                break
            
            # Check if the error is retryable
            if not is_retryable_error(e):
                # Non-retryable error, fail immediately
                break
            
            # Calculate delay
            suggested_delay = extract_retry_after(e)
            delay = retry_config.get_delay(attempt, suggested_delay)
            
            # Log the retry attempt
            error_type = "Rate limit" if any(x in str(e).lower() for x in ['rate limit', '429']) else "Error"
            if prompt_info:
                console.print(f"[yellow]{error_type} for {prompt_info}: {str(e)[:100]}...[/]")
            else:
                console.print(f"[yellow]{error_type}: {str(e)[:100]}...[/]")
            
            console.print(f"[cyan]Retrying in {delay:.1f} seconds (attempt {attempt + 1}/{retry_config.max_retries + 1})[/]")
            
            # Wait before retrying
            await asyncio.sleep(delay)
    
    # All retries exhausted
    console.print(f"[red]All retry attempts exhausted. Final error: {str(last_error)[:100]}...[/]")
    
    return {
        "success": False,
        "error": str(last_error),
        "attempts": retry_config.max_retries + 1,
        "error_type": "retryable" if is_retryable_error(last_error) else "non_retryable"
    }


