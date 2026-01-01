"use client";

import { Blog } from "@/lib/api";

interface BlogCardProps {
  blog: Blog;
  onSelect: (blog: Blog) => void;
  onDelete?: (id: string) => void;
  selected?: boolean;
}

export function BlogCard({ blog, onSelect, onDelete, selected }: BlogCardProps) {
  const formattedDate = new Date(blog.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div
      className={`card p-4 cursor-pointer transition-all ${
        selected
          ? "ring-2 ring-primary border-primary"
          : "hover:shadow-md hover:border-neutral-300"
      }`}
      onClick={() => onSelect(blog)}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-neutral-900 truncate">{blog.title}</h3>
          <div className="flex items-center gap-2 mt-1 text-sm text-neutral-500">
            <span>{formattedDate}</span>
            {blog.tags.length > 0 && (
              <>
                <span>•</span>
                <span className="truncate">{blog.tags.join(", ")}</span>
              </>
            )}
          </div>
          {blog.summary && (
            <p className="mt-2 text-sm text-neutral-600 line-clamp-2">
              {blog.summary}
            </p>
          )}
        </div>
        {onDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(blog.id);
            }}
            className="p-1.5 text-neutral-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
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
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
