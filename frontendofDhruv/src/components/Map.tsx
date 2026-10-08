'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { RouteResponse, RouteResult } from '@/lib/routingApi';

interface PolarMapProps {
  routeResponse?: RouteResponse | null;
}

const ROUTE_COLORS = [
  '#06b6d4', // cyan-500 — selected
  '#a78bfa', // violet-400 — pareto alt 1
  '#fb923c', // orange-400 — pareto alt 2
  '#4ade80', // green-400 — pareto alt 3
  '#f472b6', // pink-400 — pareto alt 4
];

function routeToGeoJSON(route: RouteResult): GeoJSON.FeatureCollection {
  const features: GeoJSON.Feature[] = route.segments.map((seg) => ({
    type: 'Feature',
    properties: {
      speed_mode: seg.speed_mode,
      speed_knots: seg.speed_knots,
      data_quality: seg.data_quality,
    },
    geometry: {
      type: 'LineString',
      coordinates: [
        [seg.start.lon, seg.start.lat],
        [seg.end.lon, seg.end.lat],
      ],
    },
  }));

  return { type: 'FeatureCollection', features };
}

export default function PolarMap({ routeResponse }: PolarMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [lng] = useState(0);
  const [lat] = useState(-90);
  const [zoom] = useState(1);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (map.current) return;

    if (mapContainer.current) {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        center: [lng, lat],
        zoom: zoom,
        projection: {
          type: 'globe',
        },
      });

      map.current.on('load', () => {
        console.log('Polar map loaded');
      });
    }
  }, [lng, lat, zoom]);

  // Render routes when response changes
  const renderRoutes = useCallback((response: RouteResponse | null) => {
    const m = map.current;
    if (!m || !m.isStyleLoaded()) return;

    // Clear existing route layers and sources
    for (let i = 0; i < 6; i++) {
      const layerId = `route-layer-${i}`;
      const sourceId = `route-source-${i}`;
      if (m.getLayer(layerId)) m.removeLayer(layerId);
      if (m.getSource(sourceId)) m.removeSource(sourceId);
    }

    // Clear markers
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];

    if (!response || response.status !== 'SUCCESS') return;

    // Draw selected route (thick, primary color)
    if (response.selected_route) {
      const geojson = routeToGeoJSON(response.selected_route);
      m.addSource('route-source-0', { type: 'geojson', data: geojson });
      m.addLayer({
        id: 'route-layer-0',
        type: 'line',
        source: 'route-source-0',
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: {
          'line-color': ROUTE_COLORS[0],
          'line-width': 3,
          'line-opacity': 0.9,
        },
      });

      // Origin marker
      const firstSeg = response.selected_route.segments[0];
      if (firstSeg) {
        const originMarker = new maplibregl.Marker({ color: '#22c55e' })
          .setLngLat([firstSeg.start.lon, firstSeg.start.lat])
          .setPopup(new maplibregl.Popup().setHTML('<b>Origin</b>'))
          .addTo(m);
        markersRef.current.push(originMarker);
      }

      // Destination marker
      const lastSeg = response.selected_route.segments[response.selected_route.segments.length - 1];
      if (lastSeg) {
        const destMarker = new maplibregl.Marker({ color: '#ef4444' })
          .setLngLat([lastSeg.end.lon, lastSeg.end.lat])
          .setPopup(new maplibregl.Popup().setHTML('<b>Destination</b>'))
          .addTo(m);
        markersRef.current.push(destMarker);
      }
    }

    // Draw alternative Pareto routes (thinner, different colors)
    if (response.pareto_routes) {
      response.pareto_routes.forEach((route, idx) => {
        // Skip if this is the selected route
        if (response.selected_route && route.route_id === response.selected_route.route_id) return;

        const sourceIdx = idx + 1;
        if (sourceIdx >= 6) return; // cap at 5 routes on map

        const geojson = routeToGeoJSON(route);
        m.addSource(`route-source-${sourceIdx}`, { type: 'geojson', data: geojson });
        m.addLayer({
          id: `route-layer-${sourceIdx}`,
          type: 'line',
          source: `route-source-${sourceIdx}`,
          layout: { 'line-join': 'round', 'line-cap': 'round' },
          paint: {
            'line-color': ROUTE_COLORS[sourceIdx % ROUTE_COLORS.length],
            'line-width': 1.5,
            'line-opacity': 0.5,
            'line-dasharray': [2, 2],
          },
        });
      });
    }

    // Fit map to route bounds
    if (response.selected_route && response.selected_route.segments.length > 0) {
      const bounds = new maplibregl.LngLatBounds();
      response.selected_route.segments.forEach((seg) => {
        bounds.extend([seg.start.lon, seg.start.lat]);
        bounds.extend([seg.end.lon, seg.end.lat]);
      });
      m.fitBounds(bounds, { padding: 80, maxZoom: 8 });
    }
  }, []);

  useEffect(() => {
    if (!map.current) return;

    if (map.current.isStyleLoaded()) {
      renderRoutes(routeResponse ?? null);
    } else {
      map.current.on('load', () => {
        renderRoutes(routeResponse ?? null);
      });
    }
  }, [routeResponse, renderRoutes]);

  return (
    <div className="w-full h-full relative">
      <div ref={mapContainer} className="absolute inset-0" />
      <div className="absolute top-4 left-4 z-10 bg-slate-900/80 p-4 rounded-xl border border-slate-700 backdrop-blur-md text-white shadow-xl">
        <h2 className="text-lg font-bold tracking-wider text-cyan-400">D.H.R.U.V.</h2>
        <p className="text-xs text-slate-300">Antarctic Route Viewer</p>
      </div>
    </div>
  );
}
