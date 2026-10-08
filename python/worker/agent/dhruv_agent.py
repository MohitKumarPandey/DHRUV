class DhruvAgentTools:
    """Tools available to the DHRUV agent. Must pull from actual backend state."""
    def inspect_environment(self) -> dict: pass
    def inspect_sea_ice_forecast(self) -> dict: pass
    def inspect_iceberg(self) -> dict: pass
    def inspect_iceberg_trajectory(self) -> dict: pass
    def inspect_vessel(self) -> dict: pass
    def generate_route(self) -> dict: pass
    def compare_routes(self) -> dict: pass
    def stress_test_route(self) -> dict: pass
    def analyze_resilience(self) -> dict: pass
    def inspect_fallback(self) -> dict: pass
    def request_replan(self) -> dict: pass
    def inspect_data_quality(self) -> dict: pass
    def historical_replay(self) -> dict: pass
    def generate_mission_report(self) -> dict: pass

class DhruvDecisionAgent:
    def __init__(self, tools: DhruvAgentTools):
        self.tools = tools
        # Agent Safety/Grounding rules applied at LLM prompt level
        self.system_prompt = """
        You are the DHRUV Decision Support Agent.
        - You must never invent coordinates, sea-ice concentration, iceberg positions, vessel state, weather values, route metrics, scientific confidence, or model performance.
        - If data is unavailable: say it is unavailable.
        - If data is stale: say it is stale.
        - If uncertainty is high: say uncertainty is high.
        - If no feasible route exists: say no feasible route was found.
        - You must never say 'guaranteed safe', 'collision-free', 'best possible route', or '100% safe'.
        - Use 'Recommended under selected policy' and explain why.
       """

    def run_query(self, user_intent: str, mission_state: dict):
        # Implementation of LangGraph pipeline:
        # Intent -> Tool Selection -> Scientific Backend Tools -> Decision Analysis -> Human-readable Explanation
        pass
