"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, Episode } from "@/lib/api";
import { ScriptViewer } from "@/components";

export default function EpisodeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [episode, setEpisode] = useState<Episode | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const episodeId = params.id as string;

  useEffect(() => {
    if (episodeId) {
      loadEpisode();
    }
  }, [episodeId]);

  const loadEpisode = async () => {
    setIsLoading(true);
    try {
      const data = await api.getEpisode(episodeId);
      setEpisode(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load episode");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this episode?")) return;
    try {
      await api.deleteEpisode(episodeId);
      router.push("/episodes");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete episode");
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !episode) {
    return (
      <div className="card p-8 text-center">
        <h2 className="text-xl font-semibold text-neutral-900 mb-2">
          Episode Not Found
        </h2>
        <p className="text-neutral-500 mb-4">{error || "The episode could not be loaded."}</p>
        <Link href="/episodes" className="btn-primary inline-block">
          Back to Episodes
        </Link>
      </div>
    );
  }

  const formattedDate = new Date(episode.created_at).toLocaleDateString(
    "en-US",
    {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    }
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link
            href="/episodes"
            className="text-sm text-neutral-500 hover:text-neutral-700 mb-2 inline-flex items-center gap-1"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Episodes
          </Link>
          <h1 className="text-2xl font-bold text-neutral-900">{episode.title}</h1>
          <p className="text-neutral-500 mt-1">{formattedDate}</p>
        </div>
        <button
          onClick={handleDelete}
          className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          Delete Episode
        </button>
      </div>

      {/* Insights */}
      {episode.insights && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {episode.insights.utilities.length > 0 && (
            <div className="card p-4">
              <h3 className="text-sm font-medium text-neutral-500 mb-2">
                Utilities
              </h3>
              <ul className="text-sm space-y-1">
                {episode.insights.utilities.slice(0, 2).map((item, i) => (
                  <li key={i} className="text-neutral-700 line-clamp-2">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {episode.insights.consumers.length > 0 && (
            <div className="card p-4">
              <h3 className="text-sm font-medium text-neutral-500 mb-2">
                Consumers
              </h3>
              <ul className="text-sm space-y-1">
                {episode.insights.consumers.slice(0, 2).map((item, i) => (
                  <li key={i} className="text-neutral-700 line-clamp-2">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {episode.insights.startups.length > 0 && (
            <div className="card p-4">
              <h3 className="text-sm font-medium text-neutral-500 mb-2">
                Startups
              </h3>
              <ul className="text-sm space-y-1">
                {episode.insights.startups.slice(0, 2).map((item, i) => (
                  <li key={i} className="text-neutral-700 line-clamp-2">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {episode.insights.regulatory.length > 0 && (
            <div className="card p-4">
              <h3 className="text-sm font-medium text-neutral-500 mb-2">
                Regulatory
              </h3>
              <ul className="text-sm space-y-1">
                {episode.insights.regulatory.slice(0, 2).map((item, i) => (
                  <li key={i} className="text-neutral-700 line-clamp-2">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Script */}
      <ScriptViewer episode={episode} />
    </div>
  );
}
