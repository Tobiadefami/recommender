"use client";
import React, { useState } from "react";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./ThemeToggle";

interface SearchInterfaceProps {
  userName: string;
  onSearch: (query: string) => void;
  recentSearches: Array<{ title: string; daysAgo: number }>;
  onViewAllSearches: () => void;
  onClearSuggestions: () => void;
}
export default function SearchInterface({
  userName,
  onSearch,
  recentSearches: recentSearches,
  onViewAllSearches: onViewAllSearches,
  onClearSuggestions,
}: SearchInterfaceProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchQuery);
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-4 md:p-8">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Recommendr</h1>
        </div>
        <ThemeToggle />
      </header>

      <main className="max-w-3xl mx-auto">
        <h2 className="text-3xl font-light mb-6">Good afternoon, {userName}</h2>

        <form onSubmit={handleSearch} className="bg-card rounded-lg p-4 mb-8">
          <Input
            className="bg-transparent border-none text-lg placeholder-muted-foreground mb-4"
            placeholder="Search for a product to get started"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>Get started with an example below</span>
          </div>
          <div className="flex flex-wrap gap-2 mt-4">
            <Button variant="secondary" size="sm">
              Generate excel formulas
            </Button>
            <Button variant="secondary" size="sm">
              Polish your prose
            </Button>
            <Button variant="secondary" size="sm">
              Generate interview questions
            </Button>
            <Button
              onClick={onClearSuggestions}
              variant="ghost"
              size="icon"
              className="text-muted-foreground"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </form>

        <div className="mb-4 flex justify-between items-center">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <Search className="w-4 h-4" />
            Your recent searches
          </h3>
          <Button
            onClick={onViewAllSearches}
            variant="link"
            size="sm"
            className="text-muted-foreground"
          >
            View all
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {recentSearches.map((search, index) => (
            <div key={index} className="bg-card p-4 rounded-lg">
              <h4 className="font-medium mb-2">{search.title}</h4>
              <p className="text-sm text-muted-foreground">
                {search.daysAgo} days ago
              </p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
