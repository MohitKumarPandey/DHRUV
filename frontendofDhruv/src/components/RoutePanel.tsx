'use client';

import React, { useState } from 'react';
import {
  generateRoute,
  RouteResponse,
  RouteRequest,
} from '@/lib/routingApi';

interface RoutePanelProps {
  onRouteGenerated: (response: RouteResponse) => void;
}

const DATA_QUALITY_COLORS: Record<string, string> = {
  GREEN: 'text-emerald-400',
  YELLOW: 'text-yellow-400',
  ORANGE: 'text-orange-400',
  RED: 'text-red-400',
  UNKNOWN: 'text-slate-400',
};

export default function RoutePanel({ onRouteGenerated }: RoutePanelProps) {
  const [originLat, setOriginLat] = useState('-76.0');
  const [originLon, setOriginLon] = useState('165.0');
  const [destLat, setDestLat] = useState('-77.5');
  const [destLon, setDestLon] = useState('168.0');
  const [policy, setPolicy] = useState<'CONSERVATIVE' | 'BALANCED' | 'EFFICIENT'>('BALANCED');
  const [algorithm, setAlgorithm] = useState<'DHRUV_MOTUS' | 'DIJKSTRA'>('DHRUV_MOTUS');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<RouteResponse | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const request: RouteRequest = {
        case_id: `case-${Date.now()}`,
        origin: { lat: parseFloat(originLat), lon: parseFloat(originLon) },
        destination: { lat: parseFloat(destLat), lon: parseFloat(destLon) },
        policy,
        algorithm,
        vessel: {
          id: 'sa-agulhas-ii',
          max_speed: 12,
          cruise_speed: 10,
          min_speed: 6,
          ice_class: 'PC6',
          maximum_operational_sic: 0.8,
        },
      };
      const result = await generateRoute(request);
      setResponse(result);
      onRouteGenerated(result);
    } catch (e: any) {
      setError(e.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const qualityColor = response ? (DATA_QUALITY_COLORS[response.data_quality] || 'text-slate-400') : '';

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-cyan-400 tracking-wider uppercase">Route Planner</h3>

      {/* Origin */}
      <div className="space-y-1">
        <label className="text-[10px] text-slate-500 uppercase tracking-wide">Origin (Lat, Lon)</label>
        <div className="flex gap-1">
          <input
            id="origin-lat"
            type="number"
            step="0.1"
            value={originLat}
            onChange={(e) => setOriginLat(e.target.value)}
            className="w-1/2 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
          <input
            id="origin-lon"
            type="number"
            step="0.1"
            value={originLon}
            onChange={(e) => setOriginLon(e.target.value)}
            className="w-1/2 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Destination */}
      <div className="space-y-1">
        <label className="text-[10px] text-slate-500 uppercase tracking-wide">Destination (Lat, Lon)</label>
        <div className="flex gap-1">
          <input
            id="dest-lat"
            type="number"
            step="0.1"
            value={destLat}
            onChange={(e) => setDestLat(e.target.value)}
            className="w-1/2 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
          <input
            id="dest-lon"
            type="number"
            step="0.1"
            value={destLon}
            onChange={(e) => setDestLon(e.target.value)}
            className="w-1/2 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Policy */}
      <div className="space-y-1">
        <label className="text-[10px] text-slate-500 uppercase tracking-wide">Policy</label>
        <select
          id="route-policy"
          value={policy}
          onChange={(e) => setPolicy(e.target.value as any)}
          className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
        >
          <option value="CONSERVATIVE">Conservative (Safety-First)</option>
          <option value="BALANCED">Balanced</option>
          <option value="EFFICIENT">Efficient (Fuel+Time)</option>
        </select>
      </div>

      {/* Algorithm */}
      <div className="space-y-1">
        <label className="text-[10px] text-slate-500 uppercase tracking-wide">Algorithm</label>
        <select
          id="route-algorithm"
          value={algorithm}
          onChange={(e) => setAlgorithm(e.target.value as any)}
          className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
        >
          <option value="DHRUV_MOTUS">DHRUV-MOTUS (Multi-Objective)</option>
          <option value="DIJKSTRA">Dijkstra (Baseline)</option>
        </select>
      </div>

      {/* Generate Button */}
      <button
        id="generate-route-btn"
        onClick={handleGenerate}
        disabled={loading}
        className={`w-full py-2 rounded-lg text-xs font-semibold tracking-wider uppercase transition-all duration-200
          ${loading
            ? 'bg-slate-700 text-slate-500 cursor-wait'
            : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-600/20 hover:shadow-cyan-500/40'
          }`}
      >
        {loading ? 'Computing Route…' : 'Generate Route'}
      </button>

      {/* Error */}
      {error && (
        <div className="text-xs text-red-400 bg-red-950/50 border border-red-800/50 rounded p-2">
          {error}
        </div>
      )}

      {/* Results */}
      {response && (
        <div className="space-y-2 border-t border-slate-700 pt-3">
          <div className="flex justify-between items-center">
            <span className="text-[10px] text-slate-500 uppercase">Status</span>
            <span className={`text-xs font-semibold ${response.status === 'SUCCESS' ? 'text-emerald-400' : 'text-red-400'}`}>
              {response.status}
            </span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-[10px] text-slate-500 uppercase">Data Quality</span>
            <span className={`text-xs font-semibold ${qualityColor}`}>
              {response.data_quality}
            </span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-[10px] text-slate-500 uppercase">Policy</span>
            <span className="text-xs text-slate-300">{response.policy_status}</span>
          </div>

          {response.execution_metrics && (
            <div className="bg-slate-800/50 rounded p-2 space-y-1">
              <div className="text-[10px] text-slate-500 uppercase mb-1">Execution Metrics</div>
              <div className="grid grid-cols-2 gap-x-2 gap-y-0.5 text-[10px]">
                <span className="text-slate-400">Runtime</span>
                <span className="text-slate-200 text-right">{response.execution_metrics.runtime_ms.toFixed(1)}ms</span>
                <span className="text-slate-400">Nodes Expanded</span>
                <span className="text-slate-200 text-right">{response.execution_metrics.nodes_expanded}</span>
                <span className="text-slate-400">Labels Created</span>
                <span className="text-slate-200 text-right">{response.execution_metrics.labels_created}</span>
                <span className="text-slate-400">Pareto Routes</span>
                <span className="text-slate-200 text-right">{response.execution_metrics.pareto_routes_found}</span>
                <span className="text-slate-400">Gate Rejections</span>
                <span className="text-slate-200 text-right">{response.execution_metrics.hard_gate_rejections}</span>
              </div>
            </div>
          )}

          {response.selected_route?.metrics && (
            <div className="bg-slate-800/50 rounded p-2 space-y-1">
              <div className="text-[10px] text-slate-500 uppercase mb-1">Selected Route</div>
              <div className="grid grid-cols-2 gap-x-2 gap-y-0.5 text-[10px]">
                <span className="text-slate-400">Distance</span>
                <span className="text-slate-200 text-right">{response.selected_route.metrics.total_distance_nm.toFixed(1)} nm</span>
                <span className="text-slate-400">Time</span>
                <span className="text-slate-200 text-right">{response.selected_route.metrics.total_time_hours.toFixed(1)} hrs</span>
                <span className="text-slate-400">Fuel</span>
                <span className="text-slate-200 text-right">{response.selected_route.metrics.total_fuel_tons.toFixed(1)} t</span>
                <span className="text-slate-400">Safety Uncertainty</span>
                <span className="text-slate-200 text-right">{response.selected_route.metrics.safety_uncertainty.toFixed(2)}</span>
              </div>
            </div>
          )}

          {response.warnings && (
            <div className="text-[10px] text-yellow-400 bg-yellow-950/30 border border-yellow-800/30 rounded p-1.5">
              ⚠ {response.warnings}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
