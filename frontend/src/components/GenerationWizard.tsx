"use client";

import { useState } from "react";
import { api, Blog, Episode, GenerationSettings } from "@/lib/api";

interface GenerationWizardProps {
  blog: Blog;
  onComplete: (episode: Episode) => void;
  onCancel: () => void;
}

export function GenerationWizard({
  blog,
  onComplete,
  onCancel,
}: GenerationWizardProps) {
  const [settings, setSettings] = useState<GenerationSettings>({
    duration: "medium",
    humor_level: 3,
    focus_areas: [],
    custom_talking_points: [],
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const focusOptions = [
    { id: "utilities", label: "Utilities" },
    { id: "consumers", label: "Consumers" },
    { id: "startups", label: "Startups" },
    { id: "regulatory", label: "Regulatory" },
  ];

  const toggleFocusArea = (area: string) => {
    setSettings((prev) => ({
      ...prev,
      focus_areas: prev.focus_areas.includes(area)
        ? prev.focus_areas.filter((a) => a !== area)
        : [...prev.focus_areas, area],
    }));
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setProgress("Analyzing blog content...");
    setError(null);

    try {
      // Simulate progress updates
      const progressSteps = [
        "Analyzing blog content...",
        "Expanding research insights...",
        "Creating script outline...",
        "Generating dialogue...",
        "Finalizing episode...",
      ];

      let stepIndex = 0;
      const progressInterval = setInterval(() => {
        stepIndex++;
        if (stepIndex < progressSteps.length) {
          setProgress(progressSteps[stepIndex]);
        }
      }, 8000);

      const episode = await api.generateEpisode(blog.id, settings);
      clearInterval(progressInterval);
      onComplete(episode);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setIsGenerating(false);
      setProgress(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Blog Summary */}
      <div className="bg-neutral-50 rounded-lg p-4">
        <h4 className="font-medium text-sm text-neutral-500 mb-1">
          Generating from:
        </h4>
        <p className="font-medium text-neutral-900">{blog.title}</p>
      </div>

      {/* Duration */}
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-2">
          Episode Duration
        </label>
        <div className="grid grid-cols-3 gap-3">
          {(["short", "medium", "long"] as const).map((duration) => (
            <button
              key={duration}
              onClick={() => setSettings((p) => ({ ...p, duration }))}
              disabled={isGenerating}
              className={`py-3 px-4 rounded-lg border text-center transition-colors ${
                settings.duration === duration
                  ? "border-primary bg-primary/5 text-primary"
                  : "border-neutral-200 hover:border-neutral-300"
              }`}
            >
              <div className="font-medium capitalize">{duration}</div>
              <div className="text-sm text-neutral-500">
                ~{duration === "short" ? 10 : duration === "medium" ? 20 : 30}{" "}
                min
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Humor Level */}
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-2">
          Humor Level: {settings.humor_level}/5
        </label>
        <input
          type="range"
          min={1}
          max={5}
          value={settings.humor_level}
          onChange={(e) =>
            setSettings((p) => ({ ...p, humor_level: parseInt(e.target.value) }))
          }
          disabled={isGenerating}
          className="w-full accent-primary"
        />
        <div className="flex justify-between text-xs text-neutral-500 mt-1">
          <span>Serious</span>
          <span>Comedy</span>
        </div>
      </div>

      {/* Focus Areas */}
      <div>
        <label className="block text-sm font-medium text-neutral-700 mb-2">
          Focus Areas (optional)
        </label>
        <div className="flex flex-wrap gap-2">
          {focusOptions.map((option) => (
            <button
              key={option.id}
              onClick={() => toggleFocusArea(option.id)}
              disabled={isGenerating}
              className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                settings.focus_areas.includes(option.id)
                  ? "bg-primary text-white"
                  : "bg-neutral-100 text-neutral-700 hover:bg-neutral-200"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Progress */}
      {isGenerating && progress && (
        <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary border-t-transparent" />
            <span className="text-primary font-medium">{progress}</span>
          </div>
          <p className="text-sm text-neutral-500 mt-2">
            This may take 1-2 minutes. Please wait...
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 pt-4">
        <button
          onClick={onCancel}
          disabled={isGenerating}
          className="flex-1 py-2.5 px-4 rounded-lg border border-neutral-200 text-neutral-700 font-medium hover:bg-neutral-50 transition-colors disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="flex-1 btn-primary py-2.5 disabled:opacity-50"
        >
          {isGenerating ? "Generating..." : "Generate Script"}
        </button>
      </div>
    </div>
  );
}
