import React from 'react';

interface Scenario {
  scenario_id: string;
  perturbation_definition: string;
}

export const HazardScenarios: React.FC<{ scenarios: Scenario[] }> = ({ scenarios }) => {
  return (
    <div className="hazard-scenarios p-4 bg-gray-800 text-white rounded">
      <h3 className="text-lg font-bold">Hazard-Future Scenarios</h3>
      {scenarios.length === 0 ? (
        <p>No scenarios loaded from backend.</p>
      ) : (
        <div className="grid gap-4">
          {scenarios.map((s, i) => (
            <div key={i} className="p-3 border border-gray-600 rounded">
              <p><strong>ID:</strong> {s.scenario_id}</p>
              <p><strong>Perturbation:</strong> {s.perturbation_definition}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
