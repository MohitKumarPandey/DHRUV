"""
DHRUV-MOTUS Pareto Label and Dominance Logic

TASK 14: Correct Pareto dominance:
  A dominates B iff A <= B in ALL primary objectives AND A < B in at least one.

Primary objectives: fuel, time, iceberg, safety_uncertainty
(sea_ice, weather, ocean are diagnostics feeding into these)

TASK 15: ε-dominance is applied during search using configured epsilon values.

TASK 16: Label cap is enforced with deterministic retention.
"""

from typing import List, Dict, Optional
import uuid
import logging

logger = logging.getLogger("DHRUV-MOTUS-Pareto")


class ParetoLabel:
    """
    A search label representing a partial (or complete) route in the MOTUS
    multi-objective A* search.
    
    Retains parent reference for route reconstruction.
    """
    def __init__(self, state, objective_vector, heuristic_value=0.0, parent_label=None):
        self.label_id = str(uuid.uuid4())
        self.state = state
        self.objective_vector = objective_vector
        self.heuristic_value = heuristic_value
        self.parent_label = parent_label  # Direct reference for reconstruction

    def dominates(self, other: 'ParetoLabel', epsilon: Dict[str, float] = None) -> bool:
        """
        Returns True if self dominates other.
        
        Standard dominance (epsilon=None):
          A dominates B iff A <= B in every primary objective
          AND A < B in at least one.
        
        ε-dominance (epsilon provided):
          A ε-dominates B iff A_i <= B_i + ε_i for all i
          AND A_j < B_j - ε_j for at least one j.
          
        Primary objectives: fuel, time, iceberg, safety_uncertainty
        """
        e_f = epsilon.get("fuel", 0.0) if epsilon else 0.0
        e_t = epsilon.get("time", 0.0) if epsilon else 0.0
        e_i = epsilon.get("iceberg", 0.0) if epsilon else 0.0
        e_s = epsilon.get("safety", 0.0) if epsilon else 0.0

        o1 = self.objective_vector
        o2 = other.objective_vector

        # Condition 1: A is no worse than B (with epsilon tolerance)
        no_worse = (
            o1.fuel <= o2.fuel + e_f and
            o1.time <= o2.time + e_t and
            o1.iceberg <= o2.iceberg + e_i and
            o1.safety_uncertainty <= o2.safety_uncertainty + e_s
        )

        # Condition 2: A is strictly better in at least one (with epsilon margin)
        strictly_better = (
            o1.fuel < o2.fuel - e_f or
            o1.time < o2.time - e_t or
            o1.iceberg < o2.iceberg - e_i or
            o1.safety_uncertainty < o2.safety_uncertainty - e_s
        )

        return no_worse and strictly_better

    def __lt__(self, other):
        """For heapq ordering."""
        return self.heuristic_value < other.heuristic_value

    def __eq__(self, other):
        if not isinstance(other, ParetoLabel):
            return False
        return self.label_id == other.label_id

    def __hash__(self):
        return hash(self.label_id)


class ParetoMetrics:
    """Tracks pruning metrics during search."""
    def __init__(self):
        self.labels_created = 0
        self.epsilon_pruned = 0
        self.cap_pruned = 0
        self.total_pruned = 0
        self.labels_before_cap = 0
        self.labels_after_cap = 0

    def to_dict(self) -> dict:
        return {
            "labels_created": self.labels_created,
            "epsilon_pruned": self.epsilon_pruned,
            "cap_pruned": self.cap_pruned,
            "total_pruned": self.total_pruned,
        }


def filter_non_dominated(
    labels: List[ParetoLabel],
    epsilon: Dict[str, float] = None,
    metrics: ParetoMetrics = None,
) -> List[ParetoLabel]:
    """
    Filter out dominated labels, retaining only the non-dominated (Pareto) set.
    
    When epsilon is provided, applies ε-dominance (TASK 15).
    Records pruning count in metrics if provided.
    """
    if not labels:
        return []

    before_count = len(labels)
    non_dominated = []

    for candidate in labels:
        is_dominated = False
        for other in labels:
            if candidate is other:
                continue
            if other.dominates(candidate, epsilon):
                is_dominated = True
                break
        if not is_dominated:
            non_dominated.append(candidate)

    pruned = before_count - len(non_dominated)
    if metrics is not None and epsilon is not None:
        metrics.epsilon_pruned += pruned
        metrics.total_pruned += pruned

    return non_dominated


def apply_label_cap(
    labels: List[ParetoLabel],
    max_labels: int,
    metrics: ParetoMetrics = None,
) -> List[ParetoLabel]:
    """
    TASK 16: Enforce label cap with deterministic retention.
    
    When len(labels) > max_labels, retains labels with lowest
    combined (time + fuel) as a tiebreaker — deterministic, not random.
    
    Records cap pruning metrics.
    """
    if len(labels) <= max_labels:
        return labels

    before_count = len(labels)
    if metrics is not None:
        metrics.labels_before_cap = before_count

    # Deterministic sort: prefer labels with lower time+fuel composite
    sorted_labels = sorted(
        labels,
        key=lambda l: l.objective_vector.time + l.objective_vector.fuel
    )
    result = sorted_labels[:max_labels]

    cap_pruned = before_count - len(result)
    if metrics is not None:
        metrics.cap_pruned += cap_pruned
        metrics.total_pruned += cap_pruned
        metrics.labels_after_cap = len(result)

    return result
