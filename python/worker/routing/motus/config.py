"""
DHRUV-MOTUS Configuration

All tunable parameters for the MOTUS multi-objective search algorithm.
These are engineering configuration values, NOT scientific truths.

Epsilon values control the granularity of Pareto-dominance pruning.
Larger epsilon => more aggressive pruning => fewer labels => faster search.
Smaller epsilon => finer Pareto front resolution => more labels => slower search.

Label caps prevent memory explosion on dense graphs.
Search limits prevent unbounded computation.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import json
import os
import logging

logger = logging.getLogger("DHRUV-MOTUS-Config")


@dataclass
class EpsilonConfig:
    """
    Epsilon thresholds for ε-dominance pruning.
    Each value defines the tolerance band for that objective.
    A label within epsilon of another in ALL objectives is considered dominated.
    
    Units:
      fuel: metric tons
      time: hours
      iceberg: probability units (0-1 scale)
      safety: uncertainty units (0-1 scale)
    """
    fuel: float = 10.0
    time: float = 1.0
    iceberg: float = 0.05
    safety: float = 0.05

    def to_dict(self) -> Dict[str, float]:
        return {
            "fuel": self.fuel,
            "time": self.time,
            "iceberg": self.iceberg,
            "safety": self.safety,
        }


@dataclass
class HeuristicConfig:
    """Controls A* guidance heuristic."""
    enabled: bool = True
    # Weight applied to heuristic — 1.0 is standard A*, >1 trades optimality for speed
    weight: float = 1.0


@dataclass
class WaitingConfig:
    """Controls whether WAIT actions are available during search."""
    enabled: bool = True
    max_wait_hours: float = 24.0
    wait_interval_hours: float = 6.0


@dataclass
class ScenarioConfig:
    """Controls stochastic scenario evaluation (future feature)."""
    enabled: bool = False
    sample_count: int = 50
    seed: Optional[int] = None


@dataclass
class DataPolicyConfig:
    """
    Controls how the algorithm handles missing or unavailable data.
    
    STRICT_REAL_DATA: Missing required data prevents route generation.
    WARN_AND_CONTINUE: Missing data produces warnings but search proceeds.
    """
    mode: str = "WARN_AND_CONTINUE"  # "STRICT_REAL_DATA" | "WARN_AND_CONTINUE"
    # If True, missing environmental data causes safety gate FAIL (conservative)
    fail_on_missing_environment: bool = False


@dataclass
class MotusConfig:
    """
    Complete configuration for the DHRUV-MOTUS search algorithm.
    
    This is an engineering configuration object — values are tunable
    parameters that control search behavior, NOT immutable scientific constants.
    """
    epsilon: EpsilonConfig = field(default_factory=EpsilonConfig)
    
    # Maximum labels retained per (node, time-bucket) state
    max_labels_per_state: int = 10
    
    # Maximum Pareto route candidates to return
    max_route_candidates: int = 20
    
    # Maximum search nodes to expand before termination
    max_search_nodes: int = 50000
    
    # H3 resolution for the routing graph
    h3_resolution: int = 3
    
    heuristic: HeuristicConfig = field(default_factory=HeuristicConfig)
    waiting: WaitingConfig = field(default_factory=WaitingConfig)
    scenario: ScenarioConfig = field(default_factory=ScenarioConfig)
    data_policy: DataPolicyConfig = field(default_factory=DataPolicyConfig)

    def validate(self) -> list:
        """Validate configuration and return list of warnings."""
        warnings = []
        if self.max_labels_per_state < 1:
            warnings.append("max_labels_per_state must be >= 1")
        if self.max_search_nodes < 1:
            warnings.append("max_search_nodes must be >= 1")
        if self.epsilon.fuel < 0:
            warnings.append("epsilon.fuel must be >= 0")
        if self.epsilon.time < 0:
            warnings.append("epsilon.time must be >= 0")
        if self.epsilon.iceberg < 0:
            warnings.append("epsilon.iceberg must be >= 0")
        if self.epsilon.safety < 0:
            warnings.append("epsilon.safety must be >= 0")
        if self.heuristic.weight < 0:
            warnings.append("heuristic.weight must be >= 0")
        return warnings

    @staticmethod
    def from_dict(d: dict) -> "MotusConfig":
        """Create config from a dictionary (e.g. loaded from JSON/YAML)."""
        cfg = MotusConfig()
        if "epsilon" in d:
            e = d["epsilon"]
            cfg.epsilon = EpsilonConfig(
                fuel=e.get("fuel", cfg.epsilon.fuel),
                time=e.get("time", cfg.epsilon.time),
                iceberg=e.get("iceberg", cfg.epsilon.iceberg),
                safety=e.get("safety", cfg.epsilon.safety),
            )
        cfg.max_labels_per_state = d.get("max_labels_per_state", cfg.max_labels_per_state)
        cfg.max_route_candidates = d.get("max_route_candidates", cfg.max_route_candidates)
        cfg.max_search_nodes = d.get("max_search_nodes", cfg.max_search_nodes)
        cfg.h3_resolution = d.get("h3_resolution", cfg.h3_resolution)
        
        if "heuristic" in d:
            h = d["heuristic"]
            cfg.heuristic = HeuristicConfig(
                enabled=h.get("enabled", cfg.heuristic.enabled),
                weight=h.get("weight", cfg.heuristic.weight),
            )
        if "waiting" in d:
            w = d["waiting"]
            cfg.waiting = WaitingConfig(
                enabled=w.get("enabled", cfg.waiting.enabled),
                max_wait_hours=w.get("max_wait_hours", cfg.waiting.max_wait_hours),
                wait_interval_hours=w.get("wait_interval_hours", cfg.waiting.wait_interval_hours),
            )
        if "scenario" in d:
            s = d["scenario"]
            cfg.scenario = ScenarioConfig(
                enabled=s.get("enabled", cfg.scenario.enabled),
                sample_count=s.get("sample_count", cfg.scenario.sample_count),
                seed=s.get("seed", cfg.scenario.seed),
            )
        if "data_policy" in d:
            dp = d["data_policy"]
            cfg.data_policy = DataPolicyConfig(
                mode=dp.get("mode", cfg.data_policy.mode),
                fail_on_missing_environment=dp.get("fail_on_missing_environment", cfg.data_policy.fail_on_missing_environment),
            )
        return cfg

    @staticmethod
    def from_file(path: str) -> "MotusConfig":
        """Load config from a JSON file."""
        if not os.path.exists(path):
            logger.warning(f"Config file not found at {path}, using defaults.")
            return MotusConfig()
        with open(path, "r") as f:
            return MotusConfig.from_dict(json.load(f))

    def to_dict(self) -> dict:
        return {
            "epsilon": self.epsilon.to_dict(),
            "max_labels_per_state": self.max_labels_per_state,
            "max_route_candidates": self.max_route_candidates,
            "max_search_nodes": self.max_search_nodes,
            "h3_resolution": self.h3_resolution,
            "heuristic": {
                "enabled": self.heuristic.enabled,
                "weight": self.heuristic.weight,
            },
            "waiting": {
                "enabled": self.waiting.enabled,
                "max_wait_hours": self.waiting.max_wait_hours,
                "wait_interval_hours": self.waiting.wait_interval_hours,
            },
            "scenario": {
                "enabled": self.scenario.enabled,
                "sample_count": self.scenario.sample_count,
                "seed": self.scenario.seed,
            },
            "data_policy": {
                "mode": self.data_policy.mode,
                "fail_on_missing_environment": self.data_policy.fail_on_missing_environment,
            },
        }
