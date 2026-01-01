"use client";

import { useState, useCallback, DragEvent, ChangeEvent } from "react";
import { api, Blog } from "@/lib/api";

interface BlogUploaderProps {
  onUpload: (blog: Blog) => void;
}

export function BlogUploader({ onUpload }: BlogUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pasteMode, setPasteMode] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    async (e: DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      setError(null);

      const file = e.dataTransfer.files[0];
      if (!file) return;

      if (!file.name.endsWith(".md") && !file.name.endsWith(".markdown")) {
        setError("Please upload a markdown file (.md)");
        return;
      }

      await uploadFile(file);
    },
    [onUpload]
  );

  const handleFileSelect = useCallback(
    async (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      if (!file.name.endsWith(".md") && !file.name.endsWith(".markdown")) {
        setError("Please upload a markdown file (.md)");
        return;
      }

      await uploadFile(file);
    },
    [onUpload]
  );

  const uploadFile = async (file: File) => {
    setIsLoading(true);
    setError(null);

    try {
      const blog = await api.uploadBlog(file);
      onUpload(blog);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasteSubmit = async () => {
    if (!title.trim() || !content.trim()) {
      setError("Please provide both title and content");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const blog = await api.createBlog(title, content);
      onUpload(blog);
      setTitle("");
      setContent("");
      setPasteMode(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Create failed");
    } finally {
      setIsLoading(false);
    }
  };

  if (pasteMode) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-medium">Paste Blog Content</h3>
          <button
            onClick={() => setPasteMode(false)}
            className="text-sm text-neutral-500 hover:text-neutral-700"
          >
            Back to upload
          </button>
        </div>

        <input
          type="text"
          placeholder="Blog Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
        />

        <textarea
          placeholder="Paste your markdown content here..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={10}
          className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono text-sm"
        />

        {error && (
          <p className="text-red-600 text-sm">{error}</p>
        )}

        <div className="flex gap-3">
          <button
            onClick={handlePasteSubmit}
            disabled={isLoading}
            className="btn-primary flex-1"
          >
            {isLoading ? "Creating..." : "Create Blog"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? "border-primary bg-primary/5"
            : "border-neutral-300 hover:border-neutral-400"
        } ${isLoading ? "opacity-50 pointer-events-none" : ""}`}
      >
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-neutral-100 flex items-center justify-center">
            <svg
              className="w-6 h-6 text-neutral-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>
          <div>
            <p className="text-neutral-600">
              {isLoading
                ? "Uploading..."
                : "Drag & drop your markdown file here"}
            </p>
            <p className="text-sm text-neutral-400 mt-1">or</p>
          </div>
          <label className="cursor-pointer">
            <span className="btn-primary inline-block">Select File</span>
            <input
              type="file"
              accept=".md,.markdown"
              onChange={handleFileSelect}
              className="hidden"
              disabled={isLoading}
            />
          </label>
        </div>
      </div>

      {error && <p className="text-red-600 text-sm text-center">{error}</p>}

      <div className="text-center">
        <button
          onClick={() => setPasteMode(true)}
          className="text-sm text-primary hover:text-primary-600"
        >
          Or paste content directly
        </button>
      </div>
    </div>
  );
}
