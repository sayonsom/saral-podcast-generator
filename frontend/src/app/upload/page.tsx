"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, Blog } from "@/lib/api";
import { BlogUploader, GenerationWizard } from "@/components";

export default function UploadPage() {
  const router = useRouter();
  const [uploadedBlog, setUploadedBlog] = useState<Blog | null>(null);

  const handleUpload = (blog: Blog) => {
    setUploadedBlog(blog);
  };

  const handleGenerationComplete = (episode: { id: string }) => {
    router.push(`/episodes/${episode.id}`);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-neutral-900">Upload Blog</h1>
        <p className="text-neutral-600 mt-1">
          Upload a markdown blog post to generate a podcast script
        </p>
      </div>

      {!uploadedBlog ? (
        <div className="card p-8">
          <BlogUploader onUpload={handleUpload} />
        </div>
      ) : (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-semibold text-neutral-900">
                {uploadedBlog.title}
              </h2>
              <p className="text-sm text-neutral-500">
                Blog uploaded successfully
              </p>
            </div>
            <button
              onClick={() => setUploadedBlog(null)}
              className="text-sm text-neutral-500 hover:text-neutral-700"
            >
              Upload different blog
            </button>
          </div>

          <GenerationWizard
            blog={uploadedBlog}
            onComplete={handleGenerationComplete}
            onCancel={() => setUploadedBlog(null)}
          />
        </div>
      )}

      {/* Tips */}
      <div className="bg-neutral-50 rounded-lg p-6">
        <h3 className="font-medium text-neutral-900 mb-3">Tips for best results</h3>
        <ul className="space-y-2 text-sm text-neutral-600">
          <li className="flex items-start gap-2">
            <span className="text-primary">&#8226;</span>
            Include specific data points and statistics for Doug and Claire to debate
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary">&#8226;</span>
            Mention regulatory implications (FERC, PUC) for richer discussion
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary">&#8226;</span>
            Cover multiple stakeholder perspectives (utilities, consumers, startups)
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary">&#8226;</span>
            Use markdown frontmatter for title, tags, and summary
          </li>
        </ul>
      </div>
    </div>
  );
}
