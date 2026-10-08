"""
DHRUV-MOTUS Safety Gates

Hard safety constraints evaluated BEFORE Pareto insertion.
A transition that fails any hard gate is immediately rejected.

Supports:
- Land intersection
- Vessel ice capability
- Configured wind limit
- Configured wave limit
- Data policy enforcement

When environmental data is UNAVAILABLE:
- Does NOT automatically pass the gate
- Applies the configured data policy
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .environment import (
    EnvironmentSnapshot,
    DataAvailability,
    DataQuality,
)
from .config import DataPolicyConfig


@dataclass
class SafetyGateResult:
    feasible: bool
    reason: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    source: Optional[str] = None
    gate_name: Optional[str] = None


@dataclass
class SafetyGateReport:
    """Aggregated result of all safety gate evaluations for a transition."""
    feasible: bool = True
    results: List[SafetyGateResult] = field(default_factory=list)
    hard_gate_rejections: int = 0
    data_warnings: List[str] = field(default_factory=list)

    def add_result(self, result: SafetyGateResult):
        self.results.append(result)
        if not result.feasible:
            self.feasible = False
            self.hard_gate_rejections += 1


def evaluate_hard_safety_gates(
    transition: dict,
    environment: EnvironmentSnapshot,
    vessel: dict,
    data_policy: DataPolicyConfig = None,
) -> SafetyGateReport:
    """
    Checks mandatory safety constraints BEFORE Pareto comparison.
    
    Gate evaluation order:
    1. Land intersection
    2. Vessel ice capability (if sea-ice data available)
    3. Wind limit (if weather data available)
    4. Wave limit (if weather data available)
    5. Data policy enforcement
    
    Returns SafetyGateReport with individual gate results.
    """
    if data_policy is None:
        data_policy = DataPolicyConfig()

    report = SafetyGateReport()

    # GATE 1: Land intersection
    if transition.get("is_land", False):
        report.add_result(SafetyGateResult(
            feasible=False,
            reason="LAND_INTERSECTION",
            gate_name="LAND",
            source="GEOGRAPHY",
        ))
        return report  # No point checking further

    # GATE 2: Vessel Ice Capability
    if environment.sea_ice.availability == DataAvailability.AVAILABLE:
        sic = environment.sea_ice.sic
        max_sic = vessel.get("maximum_operational_sic", 1.0)
        if sic is not None and sic > max_sic:
            report.add_result(SafetyGateResult(
                feasible=False,
                reason="VESSEL_ICE_LIMIT_EXCEEDED",
                value=sic,
                threshold=max_sic,
                gate_name="SEA_ICE",
                source="ENVIRONMENT_OBSERVATION",
            ))
    elif environment.sea_ice.availability == DataAvailability.UNAVAILABLE:
        if data_policy.fail_on_missing_environment:
            report.add_result(SafetyGateResult(
                feasible=False,
                reason="SEA_ICE_DATA_UNAVAILABLE",
                gate_name="SEA_ICE_DATA",
                source="DATA_POLICY",
            ))
        else:
            report.data_warnings.append("SEA_ICE_DATA_UNAVAILABLE: Gate not evaluated")

    # GATE 3: Wind limit
    wind_limit = vessel.get("max_operational_wind_kts")
    if wind_limit is not None:
        if environment.weather.availability == DataAvailability.AVAILABLE:
            wind = environment.weather.wind_speed_kts
            if wind is not None and wind > wind_limit:
                report.add_result(SafetyGateResult(
                    feasible=False,
                    reason="WIND_LIMIT_EXCEEDED",
                    value=wind,
                    threshold=wind_limit,
                    gate_name="WIND",
                    source="WEATHER_FORECAST",
                ))
        elif environment.weather.availability == DataAvailability.UNAVAILABLE:
            if data_policy.fail_on_missing_environment:
                report.add_result(SafetyGateResult(
                    feasible=False,
                    reason="WEATHER_DATA_UNAVAILABLE",
                    gate_name="WEATHER_DATA",
                    source="DATA_POLICY",
                ))
            else:
                report.data_warnings.append("WEATHER_DATA_UNAVAILABLE: Wind gate not evaluated")

    # GATE 4: Wave limit
    wave_limit = vessel.get("max_operational_wave_m")
    if wave_limit is not None:
        if environment.weather.availability == DataAvailability.AVAILABLE:
            wave = environment.weather.wave_height_m
            if wave is not None and wave > wave_limit:
                report.add_result(SafetyGateResult(
                    feasible=False,
                    reason="WAVE_LIMIT_EXCEEDED",
                    value=wave,
                    threshold=wave_limit,
                    gate_name="WAVE",
                    source="WEATHER_FORECAST",
                ))

    # Default: all gates passed
    if not report.results:
        report.add_result(SafetyGateResult(feasible=True, gate_name="ALL_PASSED"))

    return report
