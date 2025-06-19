"""
Simple unit tests for aggregation functionality that can be run with pytest.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock

# Test the aggregation configuration functions
def test_aggregation_config_defaults():
    """Test default aggregation configuration."""
    from multinear.engine.aggregation import get_aggregation_config, should_compute_aggregations
    
    # Test empty config - should return empty dict
    config = get_aggregation_config({})
    assert config == {}
    
    # Test should compute with empty config - should return False  
    assert should_compute_aggregations({}) == False
    
    # Test with aggregations config present
    config_with_agg = {
        "meta": {
            "aggregations": {
                "enabled": True
            }
        }
    }
    config = get_aggregation_config(config_with_agg)
    assert config["enabled"] == True
    assert config["display"] == True
    assert config["save_to_db"] == True
    
    # Test should compute with aggregations config present
    assert should_compute_aggregations(config_with_agg) == True


def test_aggregation_config_custom():
    """Test custom aggregation configuration."""
    from multinear.engine.aggregation import get_aggregation_config, should_compute_aggregations
    
    custom_config = {
        "meta": {
            "aggregations": {
                "enabled": False,
                "display": False,
                "custom_setting": "test"
            }
        }
    }
    
    config = get_aggregation_config(custom_config)
    assert config["enabled"] == False
    assert config["display"] == False
    assert config["save_to_db"] == True  # Should keep default
    assert config["custom_setting"] == "test"  # Should include custom
    
    # Test should compute with disabled config
    assert should_compute_aggregations(custom_config) == False


def test_extract_task_metadata():
    """Test metadata extraction from task models."""
    from multinear.engine.aggregation import extract_task_metadata
    
    # Create a mock task with valid metadata
    mock_task = Mock()
    mock_task.task_input = {
        "dataset_name": "single_dataset_a",
        "ability_type": "noise",
        "metric_type": "categorical",
        "question_id": 0
    }
    
    # Create aggregation config that requires these fields
    aggregation_config = {
        "grouping": {
            "detailed": ["dataset_name", "ability_type", "metric_type"]
        }
    }
    
    metadata = extract_task_metadata(mock_task, aggregation_config)
    
    assert metadata is not None
    assert metadata["dataset_name"] == "single_dataset_a"
    assert metadata["ability_type"] == "noise" 
    assert metadata["metric_type"] == "categorical"


def test_extract_task_metadata_invalid():
    """Test metadata extraction with invalid task data."""
    from multinear.engine.aggregation import extract_task_metadata
    
    # Create aggregation config
    aggregation_config = {
        "grouping": {
            "test": ["dataset_name", "ability_type"]
        }
    }
    
    # Create a mock task without proper metadata
    mock_task = Mock()
    mock_task.task_input = {}
    
    metadata = extract_task_metadata(mock_task, aggregation_config)
    assert metadata is None
    
    # Test with None input
    mock_task.task_input = None
    metadata = extract_task_metadata(mock_task, aggregation_config)
    assert metadata is None


def test_metric_type_variations():
    """Test that metadata extraction works with different metric types."""
    from multinear.engine.aggregation import extract_task_metadata
    
    # Create aggregation config
    aggregation_config = {
        "grouping": {
            "test": ["dataset_name", "ability_type", "metric_type"]
        }
    }
    
    test_cases = [
        "categorical",
        "numerical", 
        "reasoning",
        "custom_metric_type"
    ]
    
    for metric_type in test_cases:
        mock_task = Mock()
        mock_task.task_input = {
            "dataset_name": "single_dataset_a",
            "ability_type": "noise",
            "metric_type": metric_type,
            "question_id": 0
        }
        
        metadata = extract_task_metadata(mock_task, aggregation_config)
        assert metadata is not None
        assert metadata["metric_type"] == metric_type


def test_display_aggregations_no_crash():
    """Test that display_aggregations doesn't crash with various inputs."""
    from multinear.engine.aggregation import display_aggregations
    from rich.console import Console
    import io
    
    # Create a console that writes to a string buffer
    string_buffer = io.StringIO()
    console = Console(file=string_buffer, width=80)
    
    # Test with empty aggregations
    display_aggregations({}, console)
    
    # Test with minimal aggregations (new structure)
    minimal_aggregations = {
        "detailed": {
            "fields": ["test_field"],
            "results": {
                ("test_value",): {
                    "score": 0.85,
                    "count": 1,
                    "metadata": {"test_field": "test_value"}
                }
            }
        },
        "task_count": 1,
        "total_tasks": 1
    }
    display_aggregations(minimal_aggregations, console)
    
    # Test with full structure aggregations (new structure)
    full_aggregations = {
        "detailed": {
            "fields": ["dataset_name", "ability_type", "metric_type"],
            "results": {
                ("single_dataset_a", "noise", "categorical"): {
                    "score": 0.85,
                    "count": 3,
                    "metadata": {"dataset_name": "single_dataset_a", "ability_type": "noise", "metric_type": "categorical"}
                },
                ("single_dataset_a", "trend", "numerical"): {
                    "score": 0.75,
                    "count": 2,
                    "metadata": {"dataset_name": "single_dataset_a", "ability_type": "trend", "metric_type": "numerical"}
                }
            }
        },
        "overall_ability": {
            "fields": ["dataset_name", "ability_type"],
            "results": {
                ("single_dataset_a", "noise"): {
                    "score": 0.80,
                    "count": 5,
                    "metadata": {"dataset_name": "single_dataset_a", "ability_type": "noise"}
                }
            }
        },
        "task_count": 5,
        "total_tasks": 6
    }
    display_aggregations(full_aggregations, console)
    
    # Verify some output was generated
    output = string_buffer.getvalue()
    assert "AGGREGATION RESULTS" in output
    assert "Detailed Results" in output or "Overall Ability Results" in output


def test_generate_grouping_tuple():
    """Test grouping tuple generation."""
    from multinear.engine.aggregation import generate_grouping_tuple
    
    metadata = {
        "dataset_name": "single_dataset_a",
        "ability_type": "noise",
        "metric_type": "categorical"
    }
    
    # Test single field
    key = generate_grouping_tuple(metadata, ["dataset_name"])
    assert key == ("single_dataset_a",)
    
    # Test multiple fields
    key = generate_grouping_tuple(metadata, ["dataset_name", "ability_type"])
    assert key == ("single_dataset_a", "noise")
    
    # Test all fields
    key = generate_grouping_tuple(metadata, ["dataset_name", "ability_type", "metric_type"])
    assert key == ("single_dataset_a", "noise", "categorical")
    
    # Test missing field
    key = generate_grouping_tuple(metadata, ["dataset_name", "missing_field"])
    assert key == ("single_dataset_a", "unknown")


def test_serialize_tuple_keys():
    """Test tuple key serialization for database storage."""
    from multinear.engine.aggregation import _serialize_tuple_keys
    
    # Test with tuple keys
    results_with_tuples = {
        'fields': ['dataset_name', 'ability_type', 'metric_type'],
        'results': {
            ('single_dataset_a', 'noise', 'categorical'): {
                'score': 0.85,
                'count': 3,
                'metadata': {'dataset_name': 'single_dataset_a', 'ability_type': 'noise', 'metric_type': 'categorical'}
            },
            ('single_dataset_a', 'trend', 'numerical'): {
                'score': 0.75,
                'count': 2,
                'metadata': {'dataset_name': 'single_dataset_a', 'ability_type': 'trend', 'metric_type': 'numerical'}
            }
        }
    }
    
    serialized = _serialize_tuple_keys(results_with_tuples)
    
    # Check structure is preserved
    assert 'fields' in serialized
    assert 'results' in serialized
    assert serialized['fields'] == ['dataset_name', 'ability_type', 'metric_type']
    
    # Check tuple keys are converted to strings
    expected_keys = ['single_dataset_a__noise__categorical', 'single_dataset_a__trend__numerical']
    assert set(serialized['results'].keys()) == set(expected_keys)
    
    # Check data is preserved
    categorical_result = serialized['results']['single_dataset_a__noise__categorical']
    assert categorical_result['score'] == 0.85
    assert categorical_result['count'] == 3
    
    # Test empty results
    empty_results = {}
    assert _serialize_tuple_keys(empty_results) == {}


def test_config_driven_aggregations():
    """Test that aggregations respect config grouping settings."""
    from multinear.engine.aggregation import get_aggregation_config
    
    # Test custom grouping config
    custom_config = {
        "meta": {
            "aggregations": {
                "grouping": {
                    "detailed": ["dataset_name", "ability_type", "metric_type"],
                    "overall_ability": ["dataset_name", "ability_type"],
                    "overall_type": ["dataset_name", "metric_type"],
                    "custom_group": ["ability_type"]
                }
            }
        }
    }
    
    config = get_aggregation_config(custom_config)
    assert "grouping" in config
    assert "detailed" in config["grouping"]
    assert "custom_group" in config["grouping"]
    assert config["grouping"]["custom_group"] == ["ability_type"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])