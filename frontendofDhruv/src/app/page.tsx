'use client';

import { useState } from 'react';
import PolarMap from '@/components/Map';
import RoutePanel from '@/components/RoutePanel';
import { RouteResponse } from '@/lib/routingApi';

export default function Home() {
  const [routeResponse, setRouteResponse] = useState<RouteResponse | null>(null);

  return (
    <main className="flex h-screen w-full bg-slate-950 text-slate-200 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col z-20 shadow-2xl">
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.5)] flex items-center justify-center font-bold text-slate-900">D</div>
          <div>
            <h1 className="font-bold text-lg tracking-widest text-slate-100">D.H.R.U.V.</h1>
            <p className="text-[10px] text-cyan-400 uppercase tracking-widest">Mission Control</p>
          </div>
        </div>

        {/* Route Planner */}
        <div className="flex-1 p-4 overflow-y-auto">
          <RoutePanel onRouteGenerated={setRouteResponse} />
        </div>

        <div className="p-4 border-t border-slate-800 text-xs text-slate-500">
          SYSTEM STATUS: <span className="text-emerald-400 font-semibold">HEALTHY</span>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative">
        {/* Top Status Bar */}
        <header className="h-14 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 flex items-center px-6 justify-between z-20 absolute top-0 w-full pointer-events-none">
          <div className="flex gap-6 text-xs font-medium tracking-wide">
            <div className="flex items-center gap-2">
              <span className="text-slate-500">VESSEL:</span>
              <span className="text-slate-200">SA Agulhas II</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">ALGORITHM:</span>
              <span className="text-cyan-400">{routeResponse?.algorithm ?? 'DHRUV_MOTUS'}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">DATA:</span>
              <span className={
                routeResponse?.data_quality === 'GREEN' ? 'text-emerald-400' :
                routeResponse?.data_quality === 'RED' ? 'text-red-400' :
                routeResponse?.data_quality === 'YELLOW' ? 'text-yellow-400' :
                'text-slate-400'
              }>
                {routeResponse?.data_quality ?? '—'}
              </span>
            </div>
          </div>
          <div className="flex gap-4">
            <span className="text-xs px-2 py-1 rounded-md bg-slate-800 border border-slate-700 text-cyan-400 pointer-events-auto cursor-pointer hover:bg-slate-700">T-0 LIVE</span>
          </div>
        </header>

        {/* Map Container */}
        <div className="flex-1 relative bg-slate-950">
          <PolarMap routeResponse={routeResponse} />
        </div>
      </div>
    </main>
  );
}
