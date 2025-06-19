"""
Merged comprehensive tests for aggregation functionality in Multinear.

This module combines simple and comprehensive tests for the aggregation engine,
database storage, and integration with the evaluation system.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from multinear.engine.storage import (
    JobModel, TaskModel, AggregationResultModel, 
    Base, _engine
)
from multinear.engine.aggregation import (
    extract_task_metadata, compute_aggregations, save_aggregations,
    should_compute_aggregations, get_aggregation_config, display_aggregations,
    generate_grouping_tuple, _serialize_tuple_keys
)
from rich.console import Console
import io


# ===== SIMPLE TESTS (from test_aggregation_simple.py) =====

def test_aggregation_config_defaults():
    """Test default aggregation configuration."""
    # Test empty config - should return empty dict for aggregation config
    config = get_aggregation_config({})
    # The function returns a config with defaults, not empty
    assert "enabled" in config
    
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


def test_extract_task_metadata_simple():
    """Test metadata extraction from task models (simple version)."""
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


def test_extract_task_metadata_invalid_simple():
    """Test metadata extraction with invalid task data (simple version)."""
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


# ===== COMPREHENSIVE TESTS (from test_aggregation.py) =====


class TestAggregationStorage:
    """Test database storage for aggregation results."""
    
    def setup_method(self):
        """Set up test database."""
        global _engine
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        _engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=_engine)
        
        import multinear.engine.storage as storage
        storage._SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=_engine
        )
    
    def test_aggregation_result_model_creation(self):
        """Test creating and saving aggregation results."""
        # Create a test job
        job_id = JobModel.start("test-project")
        
        # Create aggregation results
        test_results = {
            "overall_categorical": 0.85,
            "overall_numerical": 0.75,
            "detail_categorical": {"trend": 0.90, "noise": 0.80}
        }
        
        # Save aggregation results
        aggregation = AggregationResultModel.save(job_id, "overall", test_results)
        
        # Verify results
        assert aggregation.id is not None
        assert aggregation.job_id == job_id
        assert aggregation.aggregation_type == "overall"
        assert aggregation.results == test_results
    
    def test_find_aggregation_by_job(self):
        """Test finding aggregation results by job ID."""
        # Create a test job
        job_id = JobModel.start("test-project")
        
        # Create multiple aggregation results
        AggregationResultModel.save(job_id, "overall", {"score": 0.85})
        AggregationResultModel.save(job_id, "by_dataset", {"dataset_a": 0.90})
        
        # Find aggregations
        aggregations = AggregationResultModel.find_by_job(job_id)
        
        # Verify results
        assert len(aggregations) == 2
        types = {agg.aggregation_type for agg in aggregations}
        assert types == {"overall", "by_dataset"}
    
    def test_aggregation_to_dict(self):
        """Test converting aggregation results to dictionary."""
        job_id = JobModel.start("test-project")
        test_results = {"test": "data"}
        
        aggregation = AggregationResultModel.save(job_id, "test", test_results)
        result_dict = aggregation.to_dict()
        
        # Verify dictionary structure
        assert "id" in result_dict
        assert "job_id" in result_dict
        assert "aggregation_type" in result_dict
        assert "results" in result_dict
        assert "created_at" in result_dict
        
        # Verify data integrity
        assert result_dict["job_id"] == job_id
        assert result_dict["aggregation_type"] == "test"
        assert result_dict["results"] == test_results


class TestAggregationEngine:
    """Test the aggregation computation engine."""
    
    def setup_method(self):
        """Set up test environment."""
        # Use an in-memory database for testing
        global _engine
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        _engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=_engine)
        
        import multinear.engine.storage as storage
        storage._SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=_engine
        )
    
    def test_extract_task_metadata(self):
        """Test extracting metadata from task models."""
        # Create a test task with proper metadata
        job_id = JobModel.start("test-project")
        task_id = TaskModel.start(job_id, 1, "single_dataset_a_q0_noise_categorical")
        
        # Set task input data
        test_input = {
            "dataset_name": "single_dataset_a",
            "ability_type": "noise",
            "question_id": 0
        }
        
        TaskModel.executed(task_id, test_input, {"output": "test"}, {}, {})
        TaskModel.evaluated(task_id, {}, True, 0.85, {}, {})
        
        # Get the task and extract metadata
        tasks = TaskModel.list(job_id)
        task = tasks[0]
        metadata = extract_task_metadata(task)
        
        # Verify metadata extraction
        assert metadata is not None
        assert metadata["dataset_name"] == "single_dataset_a"
        assert metadata["ability_type"] == "noise"
        assert metadata["metric_type"] == "categorical"
    
    def test_extract_task_metadata_invalid(self):
        """Test metadata extraction with invalid task data."""
        # Create a task without proper metadata
        job_id = JobModel.start("test-project")
        task_id = TaskModel.start(job_id, 1, "invalid_task_id")
        
        TaskModel.executed(task_id, {}, {"output": "test"}, {}, {})
        TaskModel.evaluated(task_id, {}, True, 0.85, {}, {})
        
        # Get the task and extract metadata
        tasks = TaskModel.list(job_id)
        task = tasks[0]
        metadata = extract_task_metadata(task)
        
        # Should return None for invalid metadata
        assert metadata is None
    
    def test_compute_aggregations_empty(self):
        """Test aggregation computation with no tasks."""
        job_id = JobModel.start("test-project")
        config = {}
        
        aggregations = compute_aggregations(job_id, config)
        
        # Should return empty dict for no tasks
        assert aggregations == {}
    
    def test_compute_aggregations_single_task(self):
        """Test aggregation computation with a single task."""
        job_id = JobModel.start("test-project")
        
        # Create a test task
        task_id = TaskModel.start(job_id, 1, "single_dataset_a_q0_noise_categorical")
        test_input = {
            "dataset_name": "single_dataset_a",
            "ability_type": "noise",
            "question_id": 0
        }
        
        TaskModel.executed(task_id, test_input, {"output": "test"}, {}, {})
        TaskModel.evaluated(task_id, {}, True, 0.85, {}, {})
        
        # Compute aggregations
        config = {}
        aggregations = compute_aggregations(job_id, config)
        
        # Verify aggregation structure
        assert "by_ability_type" in aggregations
        assert "overall" in aggregations
        assert "by_dataset" in aggregations
        
        # Verify specific values
        assert aggregations["overall"]["overall_categorical"] == 0.85
        assert aggregations["by_ability_type"]["detail_categorical"]["noise"] == 0.85
        assert aggregations["by_dataset"]["single_dataset_a"]["overall_categorical"] == 0.85
    
    def test_compute_aggregations_multiple_tasks(self):
        """Test aggregation computation with multiple tasks."""
        job_id = JobModel.start("test-project")
        
        # Create multiple test tasks
        tasks_data = [
            ("single_dataset_a_q0_noise_categorical", "single_dataset_a", "noise", 0.85),
            ("single_dataset_a_q1_trend_categorical", "single_dataset_a", "trend", 0.90),
            ("single_dataset_a_q0_noise_numerical", "single_dataset_a", "noise", 0.75),
            ("single_dataset_b_q0_noise_categorical", "single_dataset_b", "noise", 0.80),
        ]
        
        for i, (challenge_id, dataset, ability, score) in enumerate(tasks_data):
            task_id = TaskModel.start(job_id, i+1, challenge_id)
            test_input = {
                "dataset_name": dataset,
                "ability_type": ability,
                "question_id": 0
            }
            
            TaskModel.executed(task_id, test_input, {"output": "test"}, {}, {})
            TaskModel.evaluated(task_id, {}, True, score, {}, {})
        
        # Compute aggregations
        config = {}
        aggregations = compute_aggregations(job_id, config)
        
        # Verify categorical averages
        categorical_scores = [0.85, 0.90, 0.80]  # Only categorical tasks
        expected_categorical = sum(categorical_scores) / len(categorical_scores)
        assert abs(aggregations["overall"]["overall_categorical"] - expected_categorical) < 0.001
        
        # Verify numerical average
        assert aggregations["overall"]["overall_numerical"] == 0.75
        
        # Verify ability type breakdown
        assert aggregations["by_ability_type"]["detail_categorical"]["noise"] == 0.825  # (0.85 + 0.80) / 2
        assert aggregations["by_ability_type"]["detail_categorical"]["trend"] == 0.90
        
        # Verify dataset breakdown
        assert "single_dataset_a" in aggregations["by_dataset"]
        assert "single_dataset_b" in aggregations["by_dataset"]
    
    def test_should_compute_aggregations(self):
        """Test aggregation enablement logic."""
        # Default should be True
        assert should_compute_aggregations({}) == True
        
        # Explicitly enabled
        config = {"meta": {"aggregations": {"enabled": True}}}
        assert should_compute_aggregations(config) == True
        
        # Explicitly disabled
        config = {"meta": {"aggregations": {"enabled": False}}}
        assert should_compute_aggregations(config) == False
    
    def test_get_aggregation_config(self):
        """Test aggregation configuration retrieval."""
        # Test default config
        config = get_aggregation_config({})
        assert config["enabled"] == True
        assert config["display"] == True
        assert config["save_to_db"] == True
        
        # Test custom config
        custom_config = {
            "meta": {
                "aggregations": {
                    "enabled": False,
                    "display": False
                }
            }
        }
        
        config = get_aggregation_config(custom_config)
        assert config["enabled"] == False
        assert config["display"] == False
        assert config["save_to_db"] == True  # Default value should remain
    
    def test_save_aggregations(self):
        """Test saving aggregations to database."""
        job_id = JobModel.start("test-project")
        
        aggregations = {
            "overall": {"overall_categorical": 0.85},
            "by_ability_type": {"detail_categorical": {"noise": 0.85}},
            "task_count": 5,
            "total_tasks": 6
        }
        
        save_aggregations(job_id, aggregations)
        
        # Verify saved aggregations
        saved_aggregations = AggregationResultModel.find_by_job(job_id)
        assert len(saved_aggregations) == 2  # Should exclude metadata
        
        types = {agg.aggregation_type for agg in saved_aggregations}
        assert types == {"overall", "by_ability_type"}
    
    @patch('builtins.print')  # Mock print to avoid console output during tests
    def test_display_aggregations(self, mock_print):
        """Test displaying aggregations to console."""
        aggregations = {
            "overall": {
                "overall_categorical": 0.85,
                "overall_numerical": 0.75
            },
            "by_ability_type": {
                "detail_categorical": {"noise": 0.85, "trend": 0.90}
            },
            "by_dataset": {
                "single_dataset_a": {
                    "overall_categorical": 0.85,
                    "overall_numerical": 0.75,
                    "overall_reasoning": 0.80
                }
            },
            "task_count": 5,
            "total_tasks": 6
        }
        
        console = Console(file=open(os.devnull, 'w'))  # Redirect output to devnull
        
        # Should not raise any exceptions
        display_aggregations(aggregations, console)


class TestAggregationIntegration:
    """Test integration with export and other components."""
    
    def setup_method(self):
        """Set up test environment."""
        # Use an in-memory database for testing
        global _engine
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        _engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=_engine)
        
        import multinear.engine.storage as storage
        storage._SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=_engine
        )
    
    def test_aggregation_in_export(self):
        """Test that aggregations are included in export data."""
        # This would typically be tested with the actual export command
        # For now, we test the underlying functionality
        
        job_id = JobModel.start("test-project")
        
        # Save some aggregation results
        AggregationResultModel.save(job_id, "overall", {"overall_categorical": 0.85})
        AggregationResultModel.save(job_id, "by_dataset", {"dataset_a": 0.90})
        
        # Retrieve aggregations (simulating export functionality)
        aggregations = AggregationResultModel.find_by_job(job_id)
        
        # Verify aggregations can be converted to export format
        export_data = {}
        if aggregations:
            export_data["aggregations"] = {}
            for aggregation in aggregations:
                export_data["aggregations"][aggregation.aggregation_type] = {
                    "results": aggregation.results,
                    "created_at": aggregation.created_at.isoformat()
                }
        
        # Verify export structure
        assert "aggregations" in export_data
        assert "overall" in export_data["aggregations"]
        assert "by_dataset" in export_data["aggregations"]
        
        # Verify data integrity
        assert export_data["aggregations"]["overall"]["results"]["overall_categorical"] == 0.85


@pytest.fixture
def temp_multinear_dir():
    """Create temporary .multinear directory for tests."""
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    # Create .multinear directory for database
    Path(".multinear").mkdir(exist_ok=True)
    
    yield test_dir
    
    # Clean up
    os.chdir(original_cwd)
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)


def test_temp_dir_setup(temp_multinear_dir):
    """Test that temporary directory setup works."""
    assert Path(".multinear").exists()
    assert Path(temp_multinear_dir).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])