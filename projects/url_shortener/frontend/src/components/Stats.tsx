import { BarChart3, TrendingUp } from "lucide-react";
import type { StatsResponse } from ".";
import type React from "react";
import { useState } from "react";
import { API_BASE } from "../api";

interface StatsSectionProps {
  error: string;
  setError: (error: string) => void;
}

export const StatsSection: React.FC<StatsSectionProps> = ({
  // props
  setError,
}) => {
  // states
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [statsCode, setStatsCode] = useState("");
  const [loadingStats, setLoadingStats] = useState(false);

  const fetchStats = async () => {
    setLoadingStats(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/stats/${statsCode}`);

      if (!res.ok) {
        throw new Error("Stats not found");
      }

      const data: StatsResponse = await res.json();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown Error");
      setStats(null);
    } finally {
      setLoadingStats(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800 flex items-center gap-2">
        <BarChart3 className="w-6 h-6" />
        View Statistics
      </h2>

      <div className="space-y-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={statsCode}
            onChange={(e) => setStatsCode(e.target.value)}
            placeholder="Enter short code (e.g., aB3x9K)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
          <button
            onClick={fetchStats}
            disabled={loadingStats || !statsCode}
            className="bg-indigo-600 text-white py-3 px-8 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:bg-gray-400"
          >
            {loadingStats ? "Loading..." : "Get Stats"}
          </button>
        </div>
      </div>

      {stats && (
        <div className="mt-6 space-y-4">
          <div className="p-4 bg-indigo-50 rounded-lg">
            <p className="text-sm text-gray-600">Short Code</p>
            <p className="text-xl font-bold text-indigo-600">
              {stats.short_code}
            </p>
          </div>

          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-600">Original URL</p>
            <a
              href={stats.long_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline break-all"
            >
              {stats.long_url}
            </a>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <p className="text-sm text-gray-600">Total Clicks</p>
              </div>
              <p className="text-3xl font-bold text-green-600">
                {stats.clicks}
              </p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Created</p>
              <p className="text-lg font-semibold text-purple-600">
                {new Date(stats.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          {stats.last_clicked_at && (
            <div className="p-4 bg-orange-50 rounded-lg">
              <p className="text-sm text-gray-600">Last Clicked</p>
              <p className="text-lg font-semibold text-orange-600">
                {new Date(stats.last_clicked_at).toLocaleString()}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
