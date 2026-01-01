"use client";

import { useState, useEffect } from "react";
import { api, Character } from "@/lib/api";
import { CharacterCard } from "@/components";

export default function SettingsPage() {
  const [characters, setCharacters] = useState<{
    doug: Character;
    claire: Character;
  } | null>(null);
  const [callbacks, setCallbacks] = useState<
    Array<{ episode_id: string; title: string; summary: string }>
  >([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [charactersData, callbacksData] = await Promise.all([
        api.getCharacters(),
        api.getCallbacks(),
      ]);
      setCharacters(charactersData);
      setCallbacks(callbacksData);
    } catch (error) {
      console.error("Failed to load settings:", error);
    } finally {
      setIsLoading(false);
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
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Settings</h1>
        <p className="text-neutral-600 mt-1">
          View character profiles and episode callbacks
        </p>
      </div>

      {/* Characters */}
      <section>
        <h2 className="text-lg font-semibold text-neutral-900 mb-4">
          Character Profiles
        </h2>
        {characters && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <CharacterCard character={characters.doug} variant="doug" />
            <CharacterCard character={characters.claire} variant="claire" />
          </div>
        )}
      </section>

      {/* Callbacks */}
      <section>
        <h2 className="text-lg font-semibold text-neutral-900 mb-4">
          Episode Callbacks
        </h2>
        <p className="text-sm text-neutral-500 mb-4">
          Previous episode summaries used for callbacks in new episodes
        </p>

        {callbacks.length === 0 ? (
          <div className="card p-8 text-center">
            <p className="text-neutral-500">
              No episode callbacks yet. Generate episodes to build your callback history.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {callbacks.map((callback) => (
              <div key={callback.episode_id} className="card p-4">
                <h3 className="font-medium text-neutral-900 mb-1">
                  {callback.title}
                </h3>
                <p className="text-sm text-neutral-600">{callback.summary}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* API Info */}
      <section>
        <h2 className="text-lg font-semibold text-neutral-900 mb-4">
          API Configuration
        </h2>
        <div className="card p-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-neutral-500">Backend URL:</span>
              <span className="ml-2 font-mono text-neutral-700">
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              </span>
            </div>
            <div>
              <span className="text-neutral-500">Model:</span>
              <span className="ml-2 font-mono text-neutral-700">
                claude-sonnet-4
              </span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
