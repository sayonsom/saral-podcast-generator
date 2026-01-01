"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api, Blog, Episode } from "@/lib/api";
import { BlogUploader, BlogCard, EpisodeCard, GenerationWizard } from "@/components";

export default function Dashboard() {
  const router = useRouter();
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [selectedBlog, setSelectedBlog] = useState<Blog | null>(null);
  const [showGenerator, setShowGenerator] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [blogsData, episodesData] = await Promise.all([
        api.listBlogs(),
        api.listEpisodes(),
      ]);
      setBlogs(blogsData);
      setEpisodes(episodesData);
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBlogUpload = (blog: Blog) => {
    setBlogs((prev) => [blog, ...prev]);
    setSelectedBlog(blog);
    setShowGenerator(true);
  };

  const handleBlogSelect = (blog: Blog) => {
    setSelectedBlog(blog);
    setShowGenerator(true);
  };

  const handleDeleteBlog = async (id: string) => {
    try {
      await api.deleteBlog(id);
      setBlogs((prev) => prev.filter((b) => b.id !== id));
      if (selectedBlog?.id === id) {
        setSelectedBlog(null);
        setShowGenerator(false);
      }
    } catch (error) {
      console.error("Failed to delete blog:", error);
    }
  };

  const handleDeleteEpisode = async (id: string) => {
    try {
      await api.deleteEpisode(id);
      setEpisodes((prev) => prev.filter((e) => e.id !== id));
    } catch (error) {
      console.error("Failed to delete episode:", error);
    }
  };

  const handleGenerationComplete = (episode: Episode) => {
    setEpisodes((prev) => [episode, ...prev]);
    setShowGenerator(false);
    setSelectedBlog(null);
    router.push(`/episodes/${episode.id}`);
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
      {/* Hero Section */}
      <div className="text-center py-8">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">
          Energy Debates Podcast Generator
        </h1>
        <p className="text-neutral-600 max-w-2xl mx-auto">
          Transform energy industry blog posts into engaging debate-style podcast
          scripts featuring Doug and Claire.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Upload & Blogs */}
        <div className="space-y-6">
          {/* Upload Section */}
          <section className="card p-6">
            <h2 className="text-lg font-semibold mb-4">Upload New Blog</h2>
            <BlogUploader onUpload={handleBlogUpload} />
          </section>

          {/* Available Blogs */}
          {blogs.length > 0 && (
            <section className="card p-6">
              <h2 className="text-lg font-semibold mb-4">
                Available Blogs ({blogs.length})
              </h2>
              <div className="space-y-3">
                {blogs.map((blog) => (
                  <BlogCard
                    key={blog.id}
                    blog={blog}
                    onSelect={handleBlogSelect}
                    onDelete={handleDeleteBlog}
                    selected={selectedBlog?.id === blog.id}
                  />
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Right Column: Generator or Episodes */}
        <div className="space-y-6">
          {showGenerator && selectedBlog ? (
            <section className="card p-6">
              <h2 className="text-lg font-semibold mb-4">Generate Episode</h2>
              <GenerationWizard
                blog={selectedBlog}
                onComplete={handleGenerationComplete}
                onCancel={() => {
                  setShowGenerator(false);
                  setSelectedBlog(null);
                }}
              />
            </section>
          ) : (
            <section className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Recent Episodes</h2>
                {episodes.length > 0 && (
                  <a
                    href="/episodes"
                    className="text-sm text-primary hover:text-primary-600"
                  >
                    View all
                  </a>
                )}
              </div>
              {episodes.length === 0 ? (
                <div className="text-center py-8">
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
                  <p className="text-neutral-500 mb-2">No episodes yet</p>
                  <p className="text-sm text-neutral-400">
                    Upload a blog and generate your first episode
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {episodes.slice(0, 5).map((episode) => (
                    <EpisodeCard
                      key={episode.id}
                      episode={episode}
                      onDelete={handleDeleteEpisode}
                    />
                  ))}
                </div>
              )}
            </section>
          )}

          {/* Characters Preview */}
          <section className="grid grid-cols-2 gap-4">
            <div className="card p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">
                  D
                </div>
                <div>
                  <h3 className="font-medium text-sm">Doug Morrison</h3>
                  <p className="text-xs text-neutral-500">Host</p>
                </div>
              </div>
            </div>
            <div className="card p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                  C
                </div>
                <div>
                  <h3 className="font-medium text-sm">Claire Nakamura</h3>
                  <p className="text-xs text-neutral-500">Commentator</p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
