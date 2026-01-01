"use client";

import { Character } from "@/lib/api";

interface CharacterCardProps {
  character: Character;
  variant: "doug" | "claire";
}

export function CharacterCard({ character, variant }: CharacterCardProps) {
  const bgColor = variant === "doug" ? "bg-blue-100" : "bg-primary/10";
  const textColor = variant === "doug" ? "text-blue-700" : "text-primary";
  const initial = character.name.charAt(0);

  return (
    <div className="card p-6">
      <div className="flex items-center gap-3 mb-4">
        <div
          className={`w-12 h-12 rounded-full ${bgColor} flex items-center justify-center ${textColor} font-bold text-lg`}
        >
          {initial}
        </div>
        <div>
          <h3 className="font-semibold text-neutral-900">{character.name}</h3>
          <p className="text-sm text-neutral-500">{character.role}</p>
        </div>
      </div>

      <div className="space-y-4 text-sm">
        <div>
          <h4 className="font-medium text-neutral-700 mb-1">Background</h4>
          <p className="text-neutral-600">{character.background}</p>
        </div>

        <div>
          <h4 className="font-medium text-neutral-700 mb-1">Perspective</h4>
          <p className="text-neutral-600">{character.political_lean}</p>
        </div>

        <div>
          <h4 className="font-medium text-neutral-700 mb-1">Expertise</h4>
          <div className="flex flex-wrap gap-1.5">
            {character.expertise_areas.map((area) => (
              <span
                key={area}
                className={`px-2 py-0.5 rounded-full text-xs ${bgColor} ${textColor}`}
              >
                {area}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-medium text-neutral-700 mb-1">Catchphrases</h4>
          <ul className="space-y-1">
            {character.catchphrases.slice(0, 3).map((phrase, i) => (
              <li key={i} className="text-neutral-600 italic">
                &ldquo;{phrase}&rdquo;
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
