from risk.resilience import ResilienceEvaluator

def test_resilience_evaluation():
    evaluator = ResilienceEvaluator()
    assessment = evaluator.evaluate(
        expected_performance=0.9,
        tail_hazard=0.1,
        scenario_regret=0.05,
        recovery_cost=10.0,
        fallback_accessibility=1.0,
        data_confidence=0.95,
        forecast_sensitivity=0.1,
        policy_configuration="BALANCED"
    )
    
    assert assessment.scenario_stability == "HIGH"
    assert assessment.fallback_status == "AVAILABLE"
    assert assessment.tail_risk_level == "LOW"
    assert assessment.recovery_status == "EASY"
    assert assessment.overall_resilience_score > 0.8
