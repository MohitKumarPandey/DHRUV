import React from 'react';

interface ForecastData {
  valid_time: string;
  sic_prediction: number;
  data_quality: string;
}

export const SeaIceForecastTimeline: React.FC<{ forecast: ForecastData[] }> = ({ forecast }) => {
  return (
    <div className="forecast-timeline p-4 bg-gray-800 text-white rounded">
      <h3 className="text-lg font-bold">Sea-Ice Forecast Timeline</h3>
      {forecast.length === 0 ? (
        <p>No forecast data available from backend.</p>
      ) : (
        <ul>
          {forecast.map((f, i) => (
            <li key={i} className="my-2 p-2 border border-gray-600 rounded">
              <span className="font-semibold">{new Date(f.valid_time).toLocaleTimeString()}</span>: 
              SIC: {f.sic_prediction.toFixed(2)} | Quality: <span className={`text-${f.data_quality.toLowerCase()}-500`}>{f.data_quality}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
