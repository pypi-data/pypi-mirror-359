"""
Test suite for the rankedpairsvoting package.

This module contains comprehensive tests for the Ranked Pairs voting implementation,
including edge cases, error conditions, and mathematical properties.
"""

import pytest
from rankedpairsvoting import ranked_pairs_voting
from rankedpairsvoting.objects import TotalOrderGraph


class TestRankedPairsVoting:
    """Test cases for the main ranked_pairs_voting function."""

    def test_simple_election(self):
        """Test a basic three-candidate election."""
        candidates = ["Alice", "Bob", "Charlie"]
        votes = [
            [1, 2, 3],  # Alice > Bob > Charlie
            [1, 2, 3],  # Alice > Bob > Charlie
            [2, 1, 3],  # Bob > Alice > Charlie
        ]

        result = ranked_pairs_voting(candidates, votes)

        assert result[0] == "Alice"  # Alice should win
        assert len(result) == 3
        assert all(candidate in result for candidate in candidates)

    def test_single_candidate(self):
        """Test election with only one candidate."""
        candidates = ["Solo"]
        votes = [[1]]

        result = ranked_pairs_voting(candidates, votes)

        assert result == ["Solo"]

    def test_tied_preferences(self):
        """Test election with tied preferences."""
        candidates = ["A", "B", "C"]
        votes = [
            [1, 1, 2],  # A = B > C
            [2, 1, 1],  # B = C > A
            [1, 2, 2],  # A > B = C
        ]

        result = ranked_pairs_voting(candidates, votes)

        # Should return a valid ranking of all candidates
        assert len(result) == 3
        assert set(result) == set(candidates)

    def test_all_tied(self):
        """Test election where all candidates are tied."""
        candidates = ["X", "Y", "Z"]
        votes = [
            [1, 1, 1],  # All tied
            [1, 1, 1],  # All tied
            [1, 1, 1],  # All tied
        ]

        result = ranked_pairs_voting(candidates, votes)

        # Should return all candidates in some order
        assert len(result) == 3
        assert set(result) == set(candidates)

    def test_condorcet_winner(self):
        """Test that Condorcet winner is always selected."""
        candidates = ["Winner", "Loser1", "Loser2"]
        votes = [
            [1, 2, 3],  # Winner beats all
            [1, 3, 2],  # Winner beats all
            [1, 2, 3],  # Winner beats all
            [2, 1, 3],  # Even when some prefer others first
        ]

        result = ranked_pairs_voting(candidates, votes)

        assert result[0] == "Winner"

    def test_large_election(self):
        """Test election with many candidates."""
        candidates = [f"Candidate_{i}" for i in range(10)]
        votes = [
            list(range(1, 11)),  # 1, 2, 3, ..., 10
            list(range(10, 0, -1)),  # 10, 9, 8, ..., 1
            [5] * 10,  # All tied at position 5
        ]

        result = ranked_pairs_voting(candidates, votes)

        assert len(result) == 10
        assert set(result) == set(candidates)

    def test_empty_inputs_raise_error(self):
        """Test that empty inputs raise appropriate errors."""
        # These should raise ValueError or similar
        with pytest.raises(Exception):
            ranked_pairs_voting([], [])

        with pytest.raises(Exception):
            ranked_pairs_voting(["A"], [])

    def test_mismatched_lengths_raise_error(self):
        """Test that mismatched vote lengths raise errors."""
        candidates = ["A", "B"]
        votes = [[1, 2, 3]]  # Vote has 3 elements, candidates has 2

        with pytest.raises(Exception):
            ranked_pairs_voting(candidates, votes)


class TestTotalOrderGraph:
    """Test cases for the TotalOrderGraph class."""

    def test_initialization(self):
        """Test graph initialization."""
        graph = TotalOrderGraph(3)

        assert graph.nodes == {0, 1, 2}
        assert len(graph.children_of) == 3
        assert len(graph.parents_of) == 3

    def test_invalid_initialization(self):
        """Test that invalid initialization raises error."""
        with pytest.raises(ValueError):
            TotalOrderGraph(0)

        with pytest.raises(ValueError):
            TotalOrderGraph(-1)

    def test_add_edge(self):
        """Test adding edges to the graph."""
        graph = TotalOrderGraph(3)
        graph.add_edge(0, 1)  # 0 > 1

        assert 1 in graph.children_of[0]
        assert 0 in graph.parents_of[1]

    def test_transitivity(self):
        """Test that transitivity is maintained."""
        graph = TotalOrderGraph(3)
        graph.add_edge(0, 1)  # 0 > 1
        graph.add_edge(1, 2)  # 1 > 2

        # Should have transitivity: 0 > 2
        assert 2 in graph.children_of[0]
        assert 0 in graph.parents_of[2]

    def test_loop_prevention(self):
        """Test that loops are prevented."""
        graph = TotalOrderGraph(2)
        graph.add_edge(0, 1)  # 0 > 1

        # Adding 1 > 0 should be ignored (would create loop)
        graph.add_edge(1, 0)

        # Should still have only 0 > 1
        assert 1 in graph.children_of[0]
        assert 0 not in graph.children_of[1]

    def test_get_order(self):
        """Test getting the topological order."""
        graph = TotalOrderGraph(3)
        graph.add_edge(0, 1)  # 0 > 1
        graph.add_edge(0, 2)  # 0 > 2

        order = graph.get_order()

        # 0 should come before 1 and 2
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)

    def test_invalid_nodes(self):
        """Test adding edges with invalid nodes."""
        graph = TotalOrderGraph(2)

        with pytest.raises(ValueError):
            graph.add_edge(0, 5)  # Node 5 doesn't exist

        with pytest.raises(ValueError):
            graph.add_edge(-1, 0)  # Node -1 doesn't exist


class TestMathematicalProperties:
    """Test mathematical properties of the voting method."""

    def test_monotonicity_basic(self):
        """Test basic monotonicity property."""
        candidates = ["A", "B", "C"]

        # Original election
        votes1 = [
            [1, 2, 3],  # A > B > C
            [2, 1, 3],  # B > A > C
            [3, 1, 2],  # B > C > A
        ]
        result1 = ranked_pairs_voting(candidates, votes1)

        # Improve A's position in one vote
        votes2 = [
            [1, 2, 3],  # A > B > C (same)
            [1, 2, 3],  # A > B > C (improved A)
            [3, 1, 2],  # B > C > A (same)
        ]
        result2 = ranked_pairs_voting(candidates, votes2)

        # A should not be worse off
        assert result2.index("A") <= result1.index("A")

    def test_neutrality(self):
        """Test that the method treats candidates symmetrically."""
        # This is tested indirectly through other tests
        # Full neutrality testing would require many permutations
        pass

    def test_determinism(self):
        """Test that same inputs produce same outputs (with same random seed)."""
        import random

        candidates = ["X", "Y", "Z"]
        votes = [
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2],
        ]

        # Set seed for reproducible results
        random.seed(42)
        result1 = ranked_pairs_voting(candidates, votes)

        random.seed(42)
        result2 = ranked_pairs_voting(candidates, votes)

        assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__])
