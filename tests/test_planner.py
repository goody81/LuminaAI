"""Tests for the planner sanitization and DAG building functions."""
import pytest
import json
from agents.planner.main import sanitize_pddl, build_dag_from_pddl


class TestSanitizePDDL:
    """Test the sanitize_pddl function."""
    
    def test_valid_pddl_passes_sanitization(self, sample_pddl_plan):
        """Test that valid PDDL passes sanitization."""
        result = sanitize_pddl(sample_pddl_plan)
        assert result == sample_pddl_plan.strip()
    
    def test_empty_pddl_raises_error(self):
        """Test that empty PDDL raises ValueError."""
        with pytest.raises(ValueError, match="Empty PDDL plan"):
            sanitize_pddl("")
    
    def test_unbalanced_parentheses_raises_error(self, invalid_pddl_plan):
        """Test that unbalanced parentheses raise ValueError."""
        with pytest.raises(ValueError, match="Unbalanced parentheses"):
            sanitize_pddl(invalid_pddl_plan)
    
    def test_dangerous_pattern_raises_error(self, dangerous_pddl_plan):
        """Test that dangerous patterns are detected."""
        with pytest.raises(ValueError, match="dangerous pattern"):
            sanitize_pddl(dangerous_pddl_plan)
    
    def test_pddl_without_opening_paren_raises_error(self):
        """Test that PDDL not starting with '(' raises error."""
        with pytest.raises(ValueError, match="Must start with"):
            sanitize_pddl("define plan")


class TestBuildDAGFromPDDL:
    """Test the build_dag_from_pddl function."""
    
    def test_valid_pddl_creates_dag(self, sample_pddl_plan):
        """Test that valid PDDL creates a DAG."""
        result = build_dag_from_pddl(sample_pddl_plan)
        dag = json.loads(result)
        
        assert "nodes" in dag
        assert "edges" in dag
        assert "metadata" in dag
        assert isinstance(dag["nodes"], list)
        assert isinstance(dag["edges"], list)
    
    def test_dag_has_correct_structure(self, sample_pddl_plan):
        """Test that DAG has the correct structure."""
        result = build_dag_from_pddl(sample_pddl_plan)
        dag = json.loads(result)
        
        # Check nodes have required fields
        for node in dag["nodes"]:
            assert "id" in node
            assert "name" in node
            assert "type" in node
        
        # Check edges have required fields
        for edge in dag["edges"]:
            assert "from" in edge
            assert "to" in edge
    
    def test_sequential_edges_are_created(self, sample_pddl_plan):
        """Test that sequential edges are created between actions."""
        result = build_dag_from_pddl(sample_pddl_plan)
        dag = json.loads(result)
        
        # Should have N-1 edges for N nodes (sequential)
        if len(dag["nodes"]) > 1:
            assert len(dag["edges"]) >= 1
    
    def test_metadata_contains_counts(self, sample_pddl_plan):
        """Test that metadata contains node and edge counts."""
        result = build_dag_from_pddl(sample_pddl_plan)
        dag = json.loads(result)
        
        assert "metadata" in dag
        assert "node_count" in dag["metadata"]
        assert "edge_count" in dag["metadata"]
        assert dag["metadata"]["node_count"] == len(dag["nodes"])
        assert dag["metadata"]["edge_count"] == len(dag["edges"])
    
    def test_empty_pddl_returns_default_dag(self):
        """Test that empty/invalid PDDL returns a default DAG."""
        result = build_dag_from_pddl("(define (plan empty))")
        dag = json.loads(result)
        
        # Should still have a valid structure
        assert "nodes" in dag
        assert "edges" in dag
        assert len(dag["nodes"]) >= 1
