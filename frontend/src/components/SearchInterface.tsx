import React from "react";
import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./ThemeToggle";
import Autocomplete from "./Autocomplete";
import getGreeting from "@/lib/greeting";
import { SearchResult } from "@/types/search";

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
        <h2 className="text-3xl font-light mb-6">{getGreeting()}, {userName}</h2>
        <form onSubmit={onSubmit} className="bg-card rounded-lg p-4 mb-8">
          <Autocomplete
            value={searchQuery}
            onChange={onSearchQueryChange}
            onSuggestionSelect={onSuggestionSelect}
          />
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>Get started with an example below</span>
          </div>
          <div className="flex flex-wrap gap-2 mt-4">
            <Button variant="secondary" size="sm" onClick={() => onSearchQueryChange("Pixel 7 pro")}>
              Pixel 7 pro
            </Button>
            <Button variant="secondary" size="sm" onClick={() => onSearchQueryChange("Porsche taycan")}>
              Porsche taycan
            </Button>
            <Button variant="secondary" size="sm" onClick={() => onSearchQueryChange("Sony a7s iii")}>
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

        {results && (
          <div className="mt-8">
            <h2 className="text-2xl font-semibold mb-4">Search Results</h2>
            
            <div className="mb-6">
              <h3 className="text-xl font-semibold mb-2">Overall Decision</h3>
              <p>{results.overall_decision}</p>
            </div>

            <h3 className="text-xl font-semibold mb-4">Reviews</h3>
            {results.reviews.map((review, index) => (
              <div key={index} className="mb-6 p-4 bg-card rounded-lg">
                <h4 className="text-lg font-semibold mb-2">{review.product_name}</h4>
                <p className="mb-2"><strong>Source:</strong> {review.source}</p>
                <p className="mb-3">{review.review_summary}</p>

                {review.pros && review.pros.length > 0 && (
                  <div className="mb-2">
                    <strong>Pros:</strong>
                    <ul className="list-disc list-inside">
                      {review.pros.map((pro, i) => (
                        <li key={i}>{pro}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {review.cons && review.cons.length > 0 && (
                  <div className="mb-2">
                    <strong>Cons:</strong>
                    <ul className="list-disc list-inside">
                      {review.cons.map((con, i) => (
                        <li key={i}>{con}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <p><strong>Sentiment:</strong> {review.sentiment}</p>
                <p><strong>Detail Score:</strong> {review.detail_score}</p>
                <p><strong>Balanced Score:</strong> {review.balanced_score}</p>
                <p><strong>Well Written Score:</strong> {review.well_written_score}</p>
              </div>
            ))}
          </div>
        )}

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