"use client";

import Link from "next/link";
import { Episode } from "@/lib/api";

interface EpisodeCardProps {
  episode: Episode;
  onDelete?: (id: string) => void;
}

export function EpisodeCard({ episode, onDelete }: EpisodeCardProps) {
  const formattedDate = new Date(episode.created_at).toLocaleDateString(
    "en-US",
    {
      month: "short",
      day: "numeric",
      year: "numeric",
    }
  );

  return (
    <div className="card p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <Link
            href={`/episodes/${episode.id}`}
            className="block group"
          >
            <h3 className="font-medium text-neutral-900 group-hover:text-primary transition-colors truncate">
              {episode.title}
            </h3>
          </Link>
          <div className="flex items-center gap-3 mt-1 text-sm text-neutral-500">
            <span>{formattedDate}</span>
            <span>•</span>
            <span>~{episode.duration_estimate} min</span>
            <span>•</span>
            <span>Humor: {episode.humor_level}/5</span>
          </div>
          {episode.summary && (
            <p className="mt-2 text-sm text-neutral-600 line-clamp-2">
              {episode.summary}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Link
            href={`/episodes/${episode.id}`}
            className="px-3 py-1.5 text-sm bg-primary/10 text-primary rounded-md hover:bg-primary/20 transition-colors"
          >
            View
          </Link>
          {onDelete && (
            <button
              onClick={() => onDelete(episode.id)}
              className="px-3 py-1.5 text-sm text-neutral-500 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
            >
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
