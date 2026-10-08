import React from 'react';

export const MissionControl: React.FC = () => {
  return (
    <div className="mission-control bg-gray-900 text-white p-6 grid grid-cols-3 gap-4 h-full">
      <div className="col-span-2 map-container bg-black rounded shadow">
        {/* MAP VISUALIZATION (Phase 19) */}
        <h2>Live Navigation Map</h2>
        <p>Layers: vessel, planned route, alternative route, sea-ice field, iceberg observations, hazard zones, fallback corridor</p>
        <p>Animation driven by backend valid_time timestamps.</p>
      </div>
      
      <div className="sidebar grid grid-rows-4 gap-4">
        {/* CURRENT MISSION (Phase 18) */}
        <div className="panel bg-gray-800 p-4 rounded">
          <h3>Current Mission</h3>
          {/* MissionState goes here */}
        </div>
        
        {/* ROUTE COMPARISON (Phase 22) */}
        <div className="panel bg-gray-800 p-4 rounded overflow-auto">
          <h3>Route Alternatives</h3>
          <table>
            <thead>
              <tr><th>Route</th><th>ETA</th><th>Fuel</th><th>Tail Risk</th><th>Resilience</th></tr>
            </thead>
            <tbody>
              <tr><td>Alpha (Balanced)</td><td>T+48h</td><td>120</td><td>Low</td><td>High</td></tr>
              <tr><td>Beta (Efficient)</td><td>T+42h</td><td>145</td><td>Medium</td><td>Medium</td></tr>
            </tbody>
          </table>
        </div>
        
        {/* AI ASSISTANT UI (Phase 23) */}
        <div className="panel bg-gray-800 p-4 rounded">
          <h3>DHRUV AI Assistant</h3>
          <div className="chat-window h-24 bg-gray-700 p-2 mb-2 rounded">
            <p className="text-sm text-gray-300">"Why was this route selected?"</p>
            <p className="text-sm text-blue-300">"Recommended under BALANCED policy due to low tail-risk and high fallback availability."</p>
          </div>
          <input type="text" placeholder="Ask DHRUV..." className="w-full p-2 text-black" />
        </div>
      </div>
    </div>
  );
};
