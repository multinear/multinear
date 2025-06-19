"""
Comprehensive unit tests for aggregation API endpoints.

This module tests the API endpoints for retrieving aggregation results,
including schema validation, error handling, and data transformation.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock
from datetime import datetime, timezone
import json

from fastapi.testclient import TestClient
from fastapi import HTTPException

from multinear.api.router import api_router
from multinear.api.schemas import (
    AggregationResultResponse,
    AggregationSummaryResponse,
    AggregationResultData,
    AggregationGroupResult
)
from multinear.engine.storage import (
    JobModel, TaskModel, AggregationResultModel, 
    Base, _engine, TaskStatus
)


@pytest.fixture
def client():
    """Create a test client for the API."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(api_router)
    return TestClient(app)


def setup_database():
    """Set up test database with in-memory SQLite."""
    global _engine
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create new engine for tests
    _engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=_engine)
    
    # Import and update storage module
    import multinear.engine.storage as storage
    storage._engine = _engine
    storage._SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=_engine
    )


def sample_job_with_aggregations():
    """Create a sample job with aggregation data for testing."""
    # Create a test job
    job_id = JobModel.start("test-project")
    
    # Create some sample tasks
    task_data = [
        ("single_dataset_a_q0_noise_categorical", "single_dataset_a", "noise", 0.85),
        ("single_dataset_a_q1_trend_categorical", "single_dataset_a", "trend", 0.90),
        ("single_dataset_b_q0_noise_categorical", "single_dataset_b", "noise", 0.80),
    ]
    
    for i, (challenge_id, dataset, ability, score) in enumerate(task_data):
        task_id = TaskModel.start(job_id, i+1, challenge_id)
        test_input = {
            "dataset_name": dataset,
            "ability_type": ability,
            "question_id": 0
        }
        
        TaskModel.executed(task_id, test_input, {"output": "test"}, {}, {})
        TaskModel.evaluated(task_id, {}, True, score, {}, {})
    
    # Create sample aggregation results
    overall_aggregation = {
        'fields': [],
        'results': {
            'overall': {
                'score': 0.85,
                'count': 3,
                'metadata': {}
            }
        }
    }
    
    by_dataset_aggregation = {
        'fields': ['dataset_name'],
        'results': {
            'single_dataset_a': {
                'score': 0.875,
                'count': 2,
                'metadata': {'dataset_name': 'single_dataset_a'}
            },
            'single_dataset_b': {
                'score': 0.80,
                'count': 1,
                'metadata': {'dataset_name': 'single_dataset_b'}
            }
        }
    }
    
    by_ability_aggregation = {
        'fields': ['ability_type'],
        'results': {
            'noise': {
                'score': 0.825,
                'count': 2,
                'metadata': {'ability_type': 'noise'}
            },
            'trend': {
                'score': 0.90,
                'count': 1,
                'metadata': {'ability_type': 'trend'}
            }
        }
    }
    
    # Save aggregations to database
    AggregationResultModel.save(job_id, "overall", overall_aggregation)
    AggregationResultModel.save(job_id, "by_dataset", by_dataset_aggregation)
    AggregationResultModel.save(job_id, "by_ability_type", by_ability_aggregation)
    
    # Update job with task status map
    job = JobModel.find(job_id)
    job.update(
        status="completed",
        total_tasks=3,
        details={
            "status_map": {
                str(task_data[0][0]): TaskStatus.COMPLETED,
                str(task_data[1][0]): TaskStatus.COMPLETED,
                str(task_data[2][0]): TaskStatus.COMPLETED,
            }
        }
    )
    
    return job_id


class TestAggregationAPI:
    """Test cases for aggregation API endpoints."""
    
    def setup_method(self):
        """Set up test database for each test."""
        setup_database()
    
    def test_get_job_aggregations_success(self, client):
        """Test successful retrieval of all aggregations for a job."""
        job_id = sample_job_with_aggregations()
        
        response = client.get(f"/api/jobs/{job_id}/aggregations")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "job_id" in data
        assert "aggregations" in data
        assert "task_count" in data
        assert "total_tasks" in data
        
        assert data["job_id"] == job_id
        assert data["task_count"] == 3
        assert data["total_tasks"] == 3
        assert len(data["aggregations"]) == 3
        
        # Check aggregation types
        aggregation_types = {agg["aggregation_type"] for agg in data["aggregations"]}
        expected_types = {"overall", "by_dataset", "by_ability_type"}
        assert aggregation_types == expected_types
        
        # Validate aggregation structure
        for agg in data["aggregations"]:
            assert "id" in agg
            assert "job_id" in agg
            assert "aggregation_type" in agg
            assert "results" in agg
            assert "created_at" in agg
            
            # Validate results structure
            results = agg["results"]
            assert "fields" in results
            assert "results" in results
            assert isinstance(results["fields"], list)
            assert isinstance(results["results"], dict)
            
            # Validate result data points
            for key, result_data in results["results"].items():
                assert "score" in result_data
                assert "count" in result_data
                assert "metadata" in result_data
                assert isinstance(result_data["score"], (int, float))
                assert isinstance(result_data["count"], int)
    
    def test_get_job_aggregations_not_found(self, client):
        """Test retrieval of aggregations for non-existent job."""
        response = client.get("/api/jobs/nonexistent-job/aggregations")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"
    
    def test_get_job_aggregations_no_aggregations(self, client):
        """Test retrieval of aggregations for job with no aggregation data."""
        # Create a job without aggregations
        job_id = JobModel.start("test-project")
        job = JobModel.find(job_id)
        job.update(
            status="completed",
            total_tasks=0,
            details={"status_map": {}}
        )
        
        response = client.get(f"/api/jobs/{job_id}/aggregations")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["job_id"] == job_id
        assert data["aggregations"] == []
        assert data["task_count"] == 0
        assert data["total_tasks"] == 0
    
    def test_get_job_aggregation_by_type_success(self, client):
        """Test successful retrieval of specific aggregation type."""
        job_id = sample_job_with_aggregations()
        
        response = client.get(f"/api/jobs/{job_id}/aggregations/by_dataset")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "id" in data
        assert "job_id" in data
        assert "aggregation_type" in data
        assert "results" in data
        assert "created_at" in data
        
        assert data["job_id"] == job_id
        assert data["aggregation_type"] == "by_dataset"
        
        # Validate results structure
        results = data["results"]
        assert results["fields"] == ["dataset_name"]
        assert len(results["results"]) == 2
        
        # Check dataset results
        dataset_results = results["results"]
        assert "single_dataset_a" in dataset_results
        assert "single_dataset_b" in dataset_results
        
        # Validate dataset A results
        dataset_a = dataset_results["single_dataset_a"]
        assert dataset_a["score"] == 0.875
        assert dataset_a["count"] == 2
        assert dataset_a["metadata"]["dataset_name"] == "single_dataset_a"
        
        # Validate dataset B results
        dataset_b = dataset_results["single_dataset_b"]
        assert dataset_b["score"] == 0.80
        assert dataset_b["count"] == 1
        assert dataset_b["metadata"]["dataset_name"] == "single_dataset_b"
    
    def test_get_job_aggregation_by_type_not_found_job(self, client):
        """Test retrieval of specific aggregation for non-existent job."""
        response = client.get("/api/jobs/nonexistent-job/aggregations/overall")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Job not found"
    
    def test_get_job_aggregation_by_type_not_found_type(self, client):
        """Test retrieval of non-existent aggregation type for existing job."""
        job_id = sample_job_with_aggregations()
        
        response = client.get(f"/api/jobs/{job_id}/aggregations/nonexistent_type")
        
        assert response.status_code == 404
        assert "Aggregation type 'nonexistent_type' not found for job" in response.json()["detail"]
    
    def test_get_job_aggregation_overall_type(self, client):
        """Test retrieval of overall aggregation type."""
        job_id = sample_job_with_aggregations()
        
        response = client.get(f"/api/jobs/{job_id}/aggregations/overall")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["aggregation_type"] == "overall"
        assert data["results"]["fields"] == []
        
        results = data["results"]["results"]
        assert "overall" in results
        assert results["overall"]["score"] == 0.85
        assert results["overall"]["count"] == 3
    
    def test_get_job_aggregation_by_ability_type(self, client):
        """Test retrieval of by_ability_type aggregation."""
        job_id = sample_job_with_aggregations()
        
        response = client.get(f"/api/jobs/{job_id}/aggregations/by_ability_type")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["aggregation_type"] == "by_ability_type"
        assert data["results"]["fields"] == ["ability_type"]
        
        results = data["results"]["results"]
        assert "noise" in results
        assert "trend" in results
        
        # Check noise results
        noise_result = results["noise"]
        assert noise_result["score"] == 0.825
        assert noise_result["count"] == 2
        assert noise_result["metadata"]["ability_type"] == "noise"
        
        # Check trend results
        trend_result = results["trend"]
        assert trend_result["score"] == 0.90
        assert trend_result["count"] == 1
        assert trend_result["metadata"]["ability_type"] == "trend"
    
    def test_convert_aggregation_to_response_function(self, client):
        """Test the helper function that converts aggregation models to API responses."""
        from multinear.api.router import _convert_aggregation_to_response
        
        # Create test aggregation result
        job_id = JobModel.start("test-project")
        
        test_results = {
            'fields': ['dataset_name'],
            'results': {
                'dataset_a': {
                    'score': 0.85,
                    'count': 5,
                    'metadata': {'dataset_name': 'dataset_a'}
                },
                'dataset_b': {
                    'score': 0.75,
                    'count': 3,
                    'metadata': {'dataset_name': 'dataset_b'}
                }
            }
        }
        
        aggregation = AggregationResultModel.save(job_id, "by_dataset", test_results)
        
        # Convert to response format
        response = _convert_aggregation_to_response(aggregation)
        
        # Validate response
        assert isinstance(response, AggregationResultResponse)
        assert response.job_id == job_id
        assert response.aggregation_type == "by_dataset"
        assert response.results.fields == ['dataset_name']
        
        # Validate converted results
        converted_results = response.results.results
        assert len(converted_results) == 2
        assert 'dataset_a' in converted_results
        assert 'dataset_b' in converted_results
        
        # Validate dataset A data
        dataset_a = converted_results['dataset_a']
        assert isinstance(dataset_a, AggregationResultData)
        assert dataset_a.score == 0.85
        assert dataset_a.count == 5
        assert dataset_a.metadata == {'dataset_name': 'dataset_a'}
        
        # Validate dataset B data
        dataset_b = converted_results['dataset_b']
        assert isinstance(dataset_b, AggregationResultData)
        assert dataset_b.score == 0.75
        assert dataset_b.count == 3
        assert dataset_b.metadata == {'dataset_name': 'dataset_b'}


class TestAggregationAPIEdgeCases:
    """Test edge cases and error scenarios for aggregation API."""
    
    def setup_method(self):
        """Set up test database for each test."""
        setup_database()
    
    def test_job_with_partial_task_completion(self, client):
        """Test aggregations for job with mixed task completion status."""
        job_id = JobModel.start("test-project")
        
        # Create some tasks with different statuses
        task_id_1 = TaskModel.start(job_id, 1, "task_1")
        task_id_2 = TaskModel.start(job_id, 2, "task_2")
        task_id_3 = TaskModel.start(job_id, 3, "task_3")
        
        # Complete only one task
        TaskModel.executed(task_id_1, {"input": "test"}, {"output": "test"}, {}, {})
        TaskModel.evaluated(task_id_1, {}, True, 0.85, {}, {})
        
        # Update job with mixed status map
        job = JobModel.find(job_id)
        job.update(
            status="running",
            total_tasks=3,
            details={
                "status_map": {
                    "task_1": TaskStatus.COMPLETED,
                    "task_2": TaskStatus.RUNNING,
                    "task_3": TaskStatus.PENDING,
                }
            }
        )
        
        response = client.get(f"/api/jobs/{job_id}/aggregations")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should correctly count only completed tasks
        assert data["task_count"] == 1
        assert data["total_tasks"] == 3
    
    def test_empty_aggregation_results(self, client):
        """Test handling of aggregation with empty results."""
        job_id = JobModel.start("test-project")
        
        # Save aggregation with empty results
        empty_aggregation = {
            'fields': ['dataset_name'],
            'results': {}
        }
        
        AggregationResultModel.save(job_id, "empty_test", empty_aggregation)
        
        job = JobModel.find(job_id)
        job.update(
            status="completed",
            total_tasks=0,
            details={"status_map": {}}
        )
        
        response = client.get(f"/api/jobs/{job_id}/aggregations/empty_test")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["aggregation_type"] == "empty_test"
        assert data["results"]["fields"] == ["dataset_name"]
        assert data["results"]["results"] == {}
    
    def test_aggregation_with_missing_metadata(self, client):
        """Test aggregation results with missing metadata fields."""
        job_id = JobModel.start("test-project")
        
        # Create aggregation with missing metadata
        test_results = {
            'fields': ['dataset_name'],
            'results': {
                'dataset_a': {
                    'score': 0.85,
                    'count': 5
                    # Note: missing 'metadata' field
                }
            }
        }
        
        AggregationResultModel.save(job_id, "test_missing", test_results)
        
        job = JobModel.find(job_id)
        job.update(
            status="completed",
            total_tasks=5,
            details={"status_map": {"task_1": TaskStatus.COMPLETED}}
        )
        
        response = client.get(f"/api/jobs/{job_id}/aggregations/test_missing")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should handle missing metadata gracefully
        result_data = data["results"]["results"]["dataset_a"]
        assert result_data["score"] == 0.85
        assert result_data["count"] == 5
        assert result_data["metadata"] == {}  # Should default to empty dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])