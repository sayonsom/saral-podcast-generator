"use client";

import { useState } from "react";
import { Episode } from "@/lib/api";

interface ScriptViewerProps {
  episode: Episode;
}

export function ScriptViewer({ episode }: ScriptViewerProps) {
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(episode.script);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([episode.script], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${episode.title.replace(/[^a-z0-9]/gi, "_")}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Parse script into sections with speaker highlighting
  const formatScript = (script: string) => {
    const lines = script.split("\n");
    return lines.map((line, index) => {
      // Check for DOUG: or CLAIRE: lines
      if (line.startsWith("DOUG:") || line.startsWith("**DOUG:**")) {
        return (
          <div key={index} className="mb-4">
            <span className="speaker-doug font-semibold">DOUG:</span>
            <span className="text-neutral-800">
              {line.replace(/^\*?\*?DOUG:\*?\*?\s*/, "")}
            </span>
          </div>
        );
      }
      if (line.startsWith("CLAIRE:") || line.startsWith("**CLAIRE:**")) {
        return (
          <div key={index} className="mb-4">
            <span className="speaker-claire font-semibold">CLAIRE:</span>
            <span className="text-neutral-800">
              {line.replace(/^\*?\*?CLAIRE:\*?\*?\s*/, "")}
            </span>
          </div>
        );
      }
      // Timestamp markers
      if (line.match(/^\[[\d:]+\]/)) {
        return (
          <div
            key={index}
            className="text-sm text-neutral-400 font-mono my-4 border-t pt-4"
          >
            {line}
          </div>
        );
      }
      // Stage directions
      if (line.match(/^\[.*\]$/)) {
        return (
          <div key={index} className="text-sm italic text-neutral-500 my-2">
            {line}
          </div>
        );
      }
      // Headers (markdown style)
      if (line.startsWith("#")) {
        const level = line.match(/^#+/)?.[0].length || 1;
        const text = line.replace(/^#+\s*/, "");
        const className = {
          1: "text-xl font-bold mt-6 mb-3",
          2: "text-lg font-semibold mt-5 mb-2",
          3: "text-base font-medium mt-4 mb-2",
        }[level] || "font-medium mt-3 mb-1";
        return (
          <div key={index} className={className}>
            {text}
          </div>
        );
      }
      // Horizontal rules
      if (line.match(/^[-*]{3,}$/)) {
        return <hr key={index} className="my-4 border-neutral-200" />;
      }
      // Empty lines
      if (!line.trim()) {
        return <div key={index} className="h-2" />;
      }
      // Regular text
      return (
        <div key={index} className="text-neutral-700">
          {line}
        </div>
      );
    });
  };

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-neutral-500">
          ~{episode.duration_estimate} minutes • Humor: {episode.humor_level}/5
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="px-3 py-1.5 text-sm border border-neutral-200 rounded-md hover:bg-neutral-50 transition-colors flex items-center gap-1.5"
          >
            {copySuccess ? (
              <>
                <svg
                  className="w-4 h-4 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Copied!
              </>
            ) : (
              <>
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
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                Copy
              </>
            )}
          </button>
          <button
            onClick={handleDownload}
            className="px-3 py-1.5 text-sm border border-neutral-200 rounded-md hover:bg-neutral-50 transition-colors flex items-center gap-1.5"
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
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Download
          </button>
        </div>
      </div>

      {/* Script Content */}
      <div className="card p-6 max-h-[600px] overflow-y-auto">
        <div className="prose prose-neutral max-w-none">
          {formatScript(episode.script)}
        </div>
      </div>

      {/* Summary */}
      {episode.summary && (
        <div className="bg-neutral-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-neutral-500 mb-1">
            Episode Summary (for callbacks)
          </h4>
          <p className="text-neutral-700">{episode.summary}</p>
        </div>
      )}
    </div>
  );
}
