import React from "react";
import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./ThemeToggle";
import Autocomplete from "./Autocomplete";
import getGreeting from "@/lib/greeting";
import { SearchResult } from "@/types/search";
import SearchResults from "./SearchResults";

interface SearchInterfaceProps {
  userName: string;
  searchQuery: string;
  onSearchQueryChange: (query: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onSuggestionSelect: (suggestion: string) => void;
  recentSearches: Array<{ title: string; daysAgo: number }>;
  onViewAllSearches: () => void;
  onClearSuggestions: () => void;
  results: SearchResult | null;
  loading: boolean;
  showSuggestions: boolean;
}

export default function SearchInterface({
  userName,
  searchQuery,
  onSearchQueryChange,
  onSubmit,
  onSuggestionSelect,
  recentSearches,
  onViewAllSearches,
  onClearSuggestions,
  results,
  loading,
  showSuggestions,
}: SearchInterfaceProps) {
  return (
    <div className="min-h-screen bg-background text-foreground p-4 md:p-8">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Recommendr</h1>
        </div>
        <ThemeToggle />
      </header>

      <main className="max-w-3xl mx-auto">
        <h2 className="text-3xl font-light mb-6">
          {getGreeting()}, {userName}
        </h2>
        <form onSubmit={onSubmit} className="bg-card rounded-lg p-4 mb-8">
          <Autocomplete
            value={searchQuery}
            onChange={onSearchQueryChange}
            onSuggestionSelect={onSuggestionSelect}
            onSubmit={onSubmit}
            showSuggestions={showSuggestions}
          />
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>Get started with an example below</span>
          </div>
          <div className="flex flex-wrap gap-2 mt-4">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onSearchQueryChange("Pixel 7 pro")}
            >
              Pixel 7 pro
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onSearchQueryChange("Porsche taycan")}
            >
              Porsche taycan
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onSearchQueryChange("Sony a7s iii")}
            >
              Sony a7s iii
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
          <Button type="submit" className="mt-4">
            Search
          </Button>
        </form>

        {loading && <div className="text-center mt-8">Loading...</div>}

        {results && <SearchResults results={results} />}

        {!results && !loading && (
          <>
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
          </>
        )}
      </main>
    </div>
  );
}
