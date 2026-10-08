"""
Unit tests for DHRUV-MOTUS Routing Module.
Verifies algorithm execution, pareto dominance, safety gates,
route reconstruction, policy selection, and honest error handling.
"""

import unittest
import pytest
import h3

from routing.graph.builder import H3GraphBuilder
from routing.motus.algorithm import MotusAlgorithm
from routing.motus.config import MotusConfig
from routing.motus.environment import UnavailableEnvironmentProvider
from routing.motus.pareto import ParetoLabel, filter_non_dominated, apply_label_cap, ParetoMetrics
from routing.motus.objectives import MotusObjectiveVector
from routing.motus.state import RoutingState


class TestMotusAlgorithm(unittest.TestCase):
    def setUp(self):
        self.graph = H3GraphBuilder(base_resolution=3)
        # Populate small region around McMurdo / Ross Sea area (-77, 166)
        self.graph.build_region(-78.0, -75.0, 160.0, 170.0)

        self.config = MotusConfig()
        self.env = UnavailableEnvironmentProvider()
        self.algorithm = MotusAlgorithm(
            graph=self.graph,
            config=self.config,
            environment_provider=self.env,
        )

        self.vessel_profile = {
            "id": "test-vessel",
            "draft": 8.0,
            "max_speed": 12.0,
            "cruise_speed": 10.0,
            "min_speed": 6.0,
            "ice_class": "PC6",
            "maximum_operational_sic": 0.8,
            "min_fuel_rate": 1.5,
            "cruise_fuel_rate": 2.5,
            "max_fuel_rate": 4.0,
            "idle_fuel_rate": 0.5,
        }

    def test_motus_search_execution(self):
        """Test basic search execution returning Pareto labels and valid execution metrics."""
        start_lat, start_lon = -76.0, 165.0
        end_lat, end_lon = -77.0, 167.0

        pareto_labels, metrics = self.algorithm.search(
            start_lat, start_lon, end_lat, end_lon, self.vessel_profile
        )

        self.assertIsNotNone(metrics)
        self.assertGreater(metrics.runtime_ms, 0.0)
        self.assertGreaterEqual(metrics.nodes_expanded, 1)
        self.assertIn("DATA_UNAVAILABLE", metrics.warnings[0] if metrics.warnings else "")
        self.assertEqual(metrics.data_quality, "RED")

    def test_route_reconstruction(self):
        """Test that route reconstruction generates actual segments from cell chain."""
        start_lat, start_lon = -76.0, 165.0
        end_lat, end_lon = -77.0, 167.0

        pareto_labels, metrics = self.algorithm.search(
            start_lat, start_lon, end_lat, end_lon, self.vessel_profile
        )

        if pareto_labels:
            route = self.algorithm.reconstruct_route(pareto_labels[0])
            self.assertIsNotNone(route.route_id)
            self.assertGreater(len(route.segments), 0)
            self.assertEqual(route.segments[0].start_lat, start_lat)

    def test_policy_selection(self):
        """Test CONSERVATIVE, BALANCED, and EFFICIENT route selection policies."""
        start_lat, start_lon = -76.0, 165.0
        end_lat, end_lon = -77.0, 167.0

        pareto_labels, metrics = self.algorithm.search(
            start_lat, start_lon, end_lat, end_lon, self.vessel_profile
        )

        if pareto_labels:
            routes = [self.algorithm.reconstruct_route(l) for l in pareto_labels]

            selected_cons, status_cons = self.algorithm.select_route_by_policy(routes, "CONSERVATIVE")
            self.assertEqual(status_cons, "RECOMMENDED_UNDER_CONSERVATIVE_POLICY")
            self.assertIsNotNone(selected_cons)

            selected_bal, status_bal = self.algorithm.select_route_by_policy(routes, "BALANCED")
            self.assertEqual(status_bal, "RECOMMENDED_UNDER_BALANCED_POLICY")
            self.assertIsNotNone(selected_bal)

            selected_eff, status_eff = self.algorithm.select_route_by_policy(routes, "EFFICIENT")
            self.assertEqual(status_eff, "RECOMMENDED_UNDER_EFFICIENT_POLICY")
            self.assertIsNotNone(selected_eff)

    def test_pareto_dominance(self):
        """Test Pareto dominance filtering logic."""
        s1 = RoutingState("c1", 0, 0, 0, "CRUISE", 10.0, 0, 0, 0, 0, 0, 0, 0)
        s2 = RoutingState("c1", 0, 0, 0, "CRUISE", 10.0, 0, 0, 0, 0, 0, 0, 0)

        # l1 dominates l2 in all objectives (lower is better)
        o1 = MotusObjectiveVector(fuel=10.0, time=5.0, iceberg=0.1, safety_uncertainty=0.1)
        o2 = MotusObjectiveVector(fuel=15.0, time=7.0, iceberg=0.2, safety_uncertainty=0.3)

        l1 = ParetoLabel(state=s1, objective_vector=o1)
        l2 = ParetoLabel(state=s2, objective_vector=o2)

        metrics = ParetoMetrics()
        filtered = filter_non_dominated([l1, l2], metrics=metrics)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].label_id, l1.label_id)
        self.assertEqual(metrics.total_pruned, 1)


if __name__ == "__main__":
    unittest.main()
