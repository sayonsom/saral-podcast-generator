"use client";

import { useState, useEffect, useCallback } from "react";
import { api, AudioJob } from "@/lib/api";

interface AudioPanelProps {
  episodeId: string;
}

export function AudioPanel({ episodeId }: AudioPanelProps) {
  const [audioJob, setAudioJob] = useState<AudioJob | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkAudioStatus = useCallback(async () => {
    try {
      const status = await api.getEpisodeAudioStatus(episodeId);
      setAudioJob(status);
      return status;
    } catch (e) {
      console.error("Failed to check audio status:", e);
      return null;
    }
  }, [episodeId]);

  useEffect(() => {
    const loadStatus = async () => {
      setIsLoading(true);
      await checkAudioStatus();
      setIsLoading(false);
    };
    loadStatus();
  }, [checkAudioStatus]);

  // Poll for status updates when generating
  useEffect(() => {
    if (!audioJob) return;
    if (audioJob.status === "complete" || audioJob.status === "failed") return;

    const interval = setInterval(async () => {
      const status = await checkAudioStatus();
      if (status?.status === "complete" || status?.status === "failed") {
        setIsGenerating(false);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [audioJob, checkAudioStatus]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const job = await api.generateAudio(episodeId);
      setAudioJob(job);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start audio generation");
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    window.open(api.getAudioDownloadUrl(episodeId), "_blank");
  };

  if (isLoading) {
    return (
      <div className="card p-6">
        <div className="flex items-center gap-3">
          <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary border-t-transparent" />
          <span className="text-neutral-600">Loading audio status...</span>
        </div>
      </div>
    );
  }

  const isProcessing =
    audioJob &&
    ["pending", "generating", "processing"].includes(audioJob.status);

  return (
    <div className="card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-neutral-900">Audio Generation</h3>
        {audioJob?.status === "complete" && (
          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
            Ready
          </span>
        )}
        {audioJob?.status === "failed" && (
          <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded">
            Failed
          </span>
        )}
        {isProcessing && (
          <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded">
            Processing
          </span>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Progress bar when generating */}
      {isProcessing && audioJob && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-neutral-600">{audioJob.message}</span>
            <span className="font-medium text-neutral-900">{audioJob.progress}%</span>
          </div>
          <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-500"
              style={{ width: `${audioJob.progress}%` }}
            />
          </div>
          {audioJob.segment_count && (
            <p className="text-xs text-neutral-500">
              {audioJob.segment_count} audio segments
            </p>
          )}
        </div>
      )}

      {/* Completed state */}
      {audioJob?.status === "complete" && (
        <div className="space-y-4">
          <div className="flex items-center gap-4 text-sm text-neutral-600">
            {audioJob.duration_seconds && (
              <span>
                Duration: {Math.floor(audioJob.duration_seconds / 60)}:
                {String(audioJob.duration_seconds % 60).padStart(2, "0")}
              </span>
            )}
          </div>

          {/* Audio player */}
          <audio controls className="w-full" preload="metadata">
            <source src={api.getAudioDownloadUrl(episodeId)} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>

          <button onClick={handleDownload} className="btn btn-secondary w-full">
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Download MP3
          </button>
        </div>
      )}

      {/* Failed state */}
      {audioJob?.status === "failed" && (
        <div className="space-y-3">
          <p className="text-sm text-red-600">{audioJob.message}</p>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="btn btn-primary w-full"
          >
            Retry Generation
          </button>
        </div>
      )}

      {/* No audio yet */}
      {!audioJob && (
        <div className="space-y-4">
          <p className="text-sm text-neutral-600">
            Generate audio for this episode using ElevenLabs text-to-speech.
            This will create natural-sounding voices for Doug and Claire.
          </p>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="btn btn-primary w-full"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                Starting...
              </>
            ) : (
              <>
                <svg
                  className="w-4 h-4 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
                Generate Audio
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
