"use client";

import { useState, useEffect } from "react";
import { api, Episode } from "@/lib/api";
import { EpisodeCard } from "@/components";

export default function EpisodesPage() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadEpisodes();
  }, []);

  const loadEpisodes = async () => {
    setIsLoading(true);
    try {
      const data = await api.listEpisodes();
      setEpisodes(data);
    } catch (error) {
      console.error("Failed to load episodes:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this episode?")) return;
    try {
      await api.deleteEpisode(id);
      setEpisodes((prev) => prev.filter((e) => e.id !== id));
    } catch (error) {
      console.error("Failed to delete episode:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Episodes</h1>
          <p className="text-neutral-600 mt-1">
            All generated podcast scripts
          </p>
        </div>
        <a href="/" className="btn-primary">
          Generate New Episode
        </a>
      </div>

      {episodes.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-neutral-100 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-neutral-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-neutral-900 mb-2">
            No episodes yet
          </h3>
          <p className="text-neutral-500 mb-4">
            Upload a blog and generate your first podcast script
          </p>
          <a href="/" className="btn-primary inline-block">
            Get Started
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {episodes.map((episode) => (
            <EpisodeCard
              key={episode.id}
              episode={episode}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
