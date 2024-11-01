import React, { useState, useEffect } from "react";
import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./ThemeToggle";
import Autocomplete from "./Autocomplete";
import getGreeting from "@/lib/greeting";
import { SearchResult } from "@/types/search";
import SearchResults from "./SearchResults";
import LoadingCard from "./LoadingCard";
import { SearchAnalytic } from "@/types/search";
import SearchAnalytics from "./SearchAnalytics";
import { useRouter } from "next/navigation";

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
  searchAnalytics: SearchAnalytic[];
  onAnalyticSelect: (query: string) => void;
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
  searchAnalytics,
  onAnalyticSelect,
}: SearchInterfaceProps) {
  const router = useRouter();
  const [greeting, setGreeting] = useState<string>("");
  const [showAnalytics, setShowAnalytics] = useState<boolean>(false);

  useEffect(() => {
    setGreeting(getGreeting(new Date()));
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Fixed header */}
      <header className="fixed top-0 left-0 right-0 bg-background z-40 p-4 md:p-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h1
              className="text-2xl font-semibold"
              onClick={() => router.push("/")}
            >
              Recommendr
            </h1>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAnalytics(!showAnalytics)}
              className="flex items-center gap-2"
            >
              <Search className="w-4 h-4" />
              Search History
            </Button>
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* Slide-out Analytics Panel */}
      <div
        className={`fixed top-[73px] left-0 h-[calc(100vh-73px)] w-[300px] bg-background border-r transform transition-transform duration-200 ${
          showAnalytics ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="p-4 md:p-6">
          <SearchAnalytics
            recentSearches={searchAnalytics}
            onSearchSelect={onAnalyticSelect}
          />
        </div>
      </div>

      {/* Main Content */}
      <main
        className={`transition-all duration-200 ${
          showAnalytics ? "pl-[300px]" : "pl-0"
        }`}
      >
        <div className="max-w-3xl mx-auto p-4 md:p-8">
          {/* Welcome and Search Section - Always centered */}
          <div className="mt-[100px] flex flex-col items-center">
            {!results && !loading ? (
              <>
                <h2 className="text-4xl font-light mb-6 text-center">
                  {greeting}, {userName}
                </h2>

                <div className="w-full max-w-2xl">
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      onSubmit(e);
                    }}
                    className="bg-card/50 backdrop-blur-sm rounded-3xl p-8 mb-12 shadow-lg
                                border border-border/50 hover:border-border transition-colors"
                  >
                    <Autocomplete
                      value={searchQuery}
                      onChange={onSearchQueryChange}
                      onSuggestionSelect={onSuggestionSelect}
                      onSubmit={onSubmit}
                      showSuggestions={showSuggestions}
                    />
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mt-6">
                      <span>Get started with an example below</span>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-4">
                      <Button
                        variant="secondary"
                        size="sm"
                        className="rounded-xl hover:bg-accent/50 transition-colors"
                        onClick={() => onSearchQueryChange("Pixel 7 pro")}
                      >
                        Pixel 7 pro
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        className="rounded-xl hover:bg-accent/50 transition-colors"
                        onClick={() => onSearchQueryChange("Porsche taycan")}
                      >
                        Porsche taycan
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        className="rounded-xl hover:bg-accent/50 transition-colors"
                        onClick={() => onSearchQueryChange("Sony a7s iii")}
                      >
                        Sony a7s iii
                      </Button>
                      <Button
                        onClick={onClearSuggestions}
                        variant="ghost"
                        size="icon"
                        className="text-muted-foreground hover:bg-accent/50 rounded-xl"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </form>

                  {/* Recent Searches */}
                  <div className="w-full">
                    <div className="mb-4 flex justify-between items-center">
                      <h3 className="text-sm font-semibold flex items-center gap-2">
                        <Search className="w-4 h-4" />
                        Recent Searches
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
                  </div>
                </div>
              </>
            ) : (
              <div className="w-full max-w-2xl">
                {/* Search Form when results are present */}
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    onSubmit(e);
                  }}
                  className="bg-card/50 backdrop-blur-sm rounded-3xl p-8 mb-8 shadow-lg
                              border border-border/50 hover:border-border transition-colors"
                >
                  <Autocomplete
                    value={searchQuery}
                    onChange={onSearchQueryChange}
                    onSuggestionSelect={onSuggestionSelect}
                    onSubmit={onSubmit}
                    showSuggestions={showSuggestions}
                  />
                </form>

                {/* Loading State */}
                {loading && (
                  <div className="mt-8">
                    <h2 className="text-2xl font-semibold mb-4">
                      Fetching Results...
                    </h2>
                    <LoadingCard />
                    <LoadingCard />
                    <LoadingCard />
                  </div>
                )}

                {/* Search Results */}
                {results && <SearchResults results={results} />}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
