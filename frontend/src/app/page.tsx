"use client";

import { useState } from "react";

// TODO: Implement full dashboard
// See claude.md for component breakdown

export default function Home() {
  const [blogs, setBlogs] = useState<any[]>([]);
  const [episodes, setEpisodes] = useState<any[]>([]);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-primary">Energy Debates</h1>
          <nav className="flex gap-6 text-sm">
            <a href="/" className="text-neutral-900 font-medium">Dashboard</a>
            <a href="/upload" className="text-neutral-600 hover:text-neutral-900">Upload Blog</a>
            <a href="/episodes" className="text-neutral-600 hover:text-neutral-900">Episodes</a>
            <a href="/settings" className="text-neutral-600 hover:text-neutral-900">Settings</a>
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload section */}
          <section className="card p-6">
            <h2 className="text-lg font-semibold mb-4">Upload Blog</h2>
            <div className="border-2 border-dashed border-neutral-300 rounded-lg p-8 text-center">
              <p className="text-neutral-500 mb-4">Drag & drop markdown file or paste content</p>
              <button className="btn-primary">Select File</button>
            </div>
          </section>

          {/* Recent episodes */}
          <section className="card p-6">
            <h2 className="text-lg font-semibold mb-4">Recent Episodes</h2>
            {episodes.length === 0 ? (
              <p className="text-neutral-500">No episodes yet. Upload a blog to get started.</p>
            ) : (
              <ul className="space-y-3">
                {/* Episode cards go here */}
              </ul>
            )}
          </section>
        </div>

        {/* Characters preview */}
        <section className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">D</div>
              <div>
                <h3 className="font-semibold">Doug Morrison</h3>
                <p className="text-sm text-neutral-500">Host • Retired FERC Lawyer</p>
              </div>
            </div>
            <p className="text-sm text-neutral-600">Conservative, market-oriented, loves regulatory precedent. 35 years at FERC.</p>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">C</div>
              <div>
                <h3 className="font-semibold">Claire Nakamura</h3>
                <p className="text-sm text-neutral-500">Commentator • Lead at Espresso</p>
              </div>
            </div>
            <p className="text-sm text-neutral-600">Progressive, data-driven, ex-McKinsey partner. Stanford MBA, Berkeley engineering.</p>
          </div>
        </section>
      </main>
    </div>
  );
}
