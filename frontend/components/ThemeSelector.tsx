"use client";

import React from "react";
import { useTheme } from "@/lib/theme-context";
import { Palette, Moon, Sun } from "lucide-react";

export function ThemeSelector() {
  const { theme, setTheme, isDark, toggleDarkMode } = useTheme();

  const themes = [
    { id: "light", name: "Modern Blue", color: "#2563eb" },
    { id: "corporate", name: "Corporate Gray", color: "#374151" },
    { id: "purple", name: "Tech Purple", color: "#7c3aed" }
  ] as const;

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <Palette size={16} className="text-primary" />
        <h3 className="text-sm font-medium text-text-primary">Theme</h3>
      </div>

      <div className="space-y-3">
        {/* Theme selection */}
        <div className="grid grid-cols-3 gap-2">
          {themes.map((themeOption) => (
            <button
              key={themeOption.id}
              onClick={() => setTheme(themeOption.id)}
              className={`p-2 rounded-lg border text-xs transition-all ${
                theme === themeOption.id
                  ? "border-primary bg-primary text-white"
                  : "border-border hover:border-primary"
              }`}
            >
              <div
                className="w-4 h-4 rounded-full mx-auto mb-1"
                style={{ backgroundColor: themeOption.color }}
              />
              {themeOption.name}
            </button>
          ))}
        </div>

        {/* Dark mode toggle */}
        <button
          onClick={toggleDarkMode}
          className={`w-full flex items-center justify-center space-x-2 p-2 rounded-lg border transition-all ${
            isDark
              ? "border-primary bg-primary text-white"
              : "border-border hover:border-primary"
          }`}
        >
          {isDark ? <Sun size={16} /> : <Moon size={16} />}
          <span className="text-sm">{isDark ? "Light Mode" : "Dark Mode"}</span>
        </button>
      </div>
    </div>
  );
}
