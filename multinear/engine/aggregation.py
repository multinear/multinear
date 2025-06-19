"""
Generic aggregation engine for computing aggregate metrics across evaluation tasks.

This module provides a fully configurable aggregation system that:
- Extracts metadata fields based on configuration (no hardcoded field names)
- Groups tasks according to configurable grouping criteria
- Computes aggregate statistics for any combination of metadata fields
- Returns empty results if aggregations config is absent
- Is completely generic and works with any field names or evaluation domains
"""

from typing import Dict, List, Any, Optional
import statistics
from rich.console import Console
from rich.table import Table

from .storage import TaskModel, AggregationResultModel


def extract_task_metadata(task: TaskModel, aggregation_config: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Extract metadata from a task for aggregation purposes based on configuration.
    
    Args:
        task: TaskModel instance
        aggregation_config: Aggregation configuration containing grouping fields
        
    Returns:
        Dict with metadata fields or None if not available
    """
    if not task.task_input or not isinstance(task.task_input, dict):
        return None
    
    try:
        # Get all unique fields mentioned in any grouping
        all_fields = set()
        grouping_config = aggregation_config.get('grouping', {})
        for group_fields in grouping_config.values():
            all_fields.update(group_fields)
        
        # Extract only the fields that are configured
        metadata = {}
        for field in all_fields:
            if field in task.task_input:
                metadata[field] = str(task.task_input[field])
        
        return metadata if metadata else None
    except Exception:
        return None


def generate_grouping_tuple(metadata: Dict[str, str], grouping_fields: List[str]) -> tuple:
    """
    Generate a grouping tuple from task metadata based on specified fields.
    
    Args:
        metadata: Task metadata containing fields as specified in config
        grouping_fields: List of fields to use for grouping
        
    Returns:
        Tuple of field values for grouping
    """
    key_parts = []
    for field in grouping_fields:
        if field in metadata:
            key_parts.append(metadata[field])
        else:
            key_parts.append('unknown')
    return tuple(key_parts)


def compute_aggregations(job_id: str, config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Compute aggregated metrics for a completed job based on configuration.
    
    Args:
        job_id: Job ID to compute aggregations for
        config: Configuration dictionary containing aggregation settings
        
    Returns:
        Dict containing aggregated results
    """
    # Get aggregation configuration
    aggregation_config = get_aggregation_config(config)
    grouping_config = aggregation_config.get('grouping', {})
    
    # If no grouping config, return empty results
    if not grouping_config:
        return {}
    
    # Get all completed tasks for the job
    tasks = TaskModel.list(job_id)
    completed_tasks = [task for task in tasks if task.eval_score is not None]
    
    if not completed_tasks:
        return {}
    
    # Initialize aggregation structures for each grouping
    aggregation_groups = {}
    for group_name, group_fields in grouping_config.items():
        aggregation_groups[group_name] = {
            'fields': group_fields,
            'data': {}
        }
    
    # Process each task
    for task in completed_tasks:
        metadata = extract_task_metadata(task, aggregation_config)
        if not metadata:
            continue
        
        score = task.eval_score
        
        # Add task to each configured grouping
        for group_name, group_fields in grouping_config.items():
            group_key = generate_grouping_tuple(metadata, group_fields)
            
            if group_key not in aggregation_groups[group_name]['data']:
                aggregation_groups[group_name]['data'][group_key] = []
            
            # Store both score and metadata for later processing
            aggregation_groups[group_name]['data'][group_key].append({
                'score': score,
                'metadata': metadata
            })
    
    # Compute averages for each grouping
    aggregated_results = {}
    
    for group_name, group_info in aggregation_groups.items():
        group_fields = group_info['fields']
        group_data = group_info['data']
        
        group_results = {
            'fields': group_fields,
            'results': {}
        }
        
        for group_key, task_list in group_data.items():
            if not task_list:
                continue
                
            # Extract just the scores for averaging
            scores = [task['score'] for task in task_list]
            avg_score = round(statistics.mean(scores), 4)
            
            # Store result with group key tuple
            group_results['results'][group_key] = {
                'score': avg_score,
                'count': len(scores),
                'metadata': task_list[0]['metadata']  # Keep one metadata sample for reference
            }
        
        aggregated_results[group_name] = group_results
    
    # Add task statistics
    aggregated_results['task_count'] = len(completed_tasks)
    aggregated_results['total_tasks'] = len(tasks)
    
    return aggregated_results


def save_aggregations(job_id: str, aggregations: Dict[str, Any]) -> None:
    """
    Save aggregation results to the database.
    
    Args:
        job_id: Job ID
        aggregations: Aggregated results to save
    """
    for aggregation_type, results in aggregations.items():
        if aggregation_type not in ['task_count', 'total_tasks']:  # Skip metadata
            # Serialize tuple keys for database storage
            serialized_results = _serialize_tuple_keys(results)
            AggregationResultModel.save(job_id, aggregation_type, serialized_results)


def _serialize_tuple_keys(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert tuple keys to string keys for JSON serialization.
    
    Args:
        results: Results dict with potential tuple keys
        
    Returns:
        Results dict with string keys
    """
    if not results or 'results' not in results:
        return results
    
    # Keep the fields metadata and convert tuple keys to strings
    serialized = {
        'fields': results.get('fields', []),
        'results': {}
    }
    
    # Convert each tuple key to a string representation
    for group_key, data in results['results'].items():
        if isinstance(group_key, tuple):
            # Convert tuple to string with delimiter
            string_key = '__'.join(str(item) for item in group_key)
        else:
            string_key = str(group_key)
        
        serialized['results'][string_key] = data
    
    return serialized


def display_aggregations(aggregations: Dict[str, Any], console: Console) -> None:
    """
    Display aggregation results to the console.
    
    Args:
        aggregations: Aggregated results to display
        console: Rich console for output
    """
    console.print("\n[bold blue]═══ AGGREGATION RESULTS ═══[/bold blue]")
    
    # Task statistics
    task_count = aggregations.get('task_count', 0)
    total_tasks = aggregations.get('total_tasks', 0)
    console.print(f"\n[bold white]Tasks:[/bold white] {task_count} evaluated / {total_tasks} total")
    
    # Display results for each grouping
    for group_name, group_info in aggregations.items():
        if group_name in ['task_count', 'total_tasks']:
            continue
        
        if not group_info or 'results' not in group_info:
            continue
        
        group_fields = group_info.get('fields', [])
        group_results = group_info.get('results', {})
        
        if not group_results:
            continue
            
        console.print(f"\n[bold green]{group_name.replace('_', ' ').title()} Results:[/bold green]")
        
        # Create table with dynamic columns based on grouping fields
        table = Table(show_header=True, header_style="bold magenta")
        
        # Add column for each grouping field
        for field in group_fields:
            # Make field names more readable
            field_display = field.replace('_', ' ').title()
            table.add_column(field_display, style="cyan")
        
        # Add score and count columns
        table.add_column("Score", justify="right", style="green")
        table.add_column("Count", justify="right", style="yellow")
        
        # Sort by group key tuple (for consistent ordering)
        sorted_results = sorted(group_results.items(), key=lambda x: x[0])
        
        for group_key, data in sorted_results:
            # Create row with each field value in its own column
            row_values = list(group_key)  # Convert tuple to list
            row_values.append(f"{data['score']:.4f}")  # Add score
            row_values.append(str(data['count']))       # Add count
            
            table.add_row(*row_values)
        
        console.print(table)
        
        # Show summary statistics for this grouping
        scores = [data['score'] for data in group_results.values()]
        if scores:
            avg_score = round(statistics.mean(scores), 4)
            console.print(f"  [dim]Average: {avg_score:.4f}, Groups: {len(scores)}[/dim]")
    
    console.print("[bold blue]═══════════════════════════[/bold blue]\n")


def should_compute_aggregations(config: Dict[str, Any]) -> bool:
    """
    Check if aggregations should be computed based on configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if aggregations should be computed
    """
    # Check if aggregations config exists
    aggregations_config = config.get('meta', {}).get('aggregations')
    
    # Return False if aggregations config is absent
    if not aggregations_config:
        return False
    
    # Return enabled flag (default to True if enabled is not specified)
    return aggregations_config.get('enabled', True)


def get_aggregation_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get aggregation configuration with defaults.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Aggregation configuration
    """
    default_config = {
        'enabled': True,
        'display': True,
        'save_to_db': True,
        'include_in_export': True
    }
    
    aggregations_config = config.get('meta', {}).get('aggregations')
    
    # Return empty config if aggregations section is absent
    if not aggregations_config:
        return {}
    
    return {**default_config, **aggregations_config}