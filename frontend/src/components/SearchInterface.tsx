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
  {
    const [greeting, setGreeting] = useState<string>("");
    const [showAnalytics, setShowAnalytics] = useState<boolean>(false);

    useEffect(() => {
      setGreeting(getGreeting(new Date()));
    }, []);
    return (
      <div className="min-h-screen bg-background text-foreground">
        {/* Fixed header */}
        <header className="fixed top-0 left-0 right-0 bg-background z-10 p-4 md:p-8 border-b">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-semibold">Recommendr</h1>
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
          className={`fixed top-[73px] left-0 h-[calc(100vh-73px)] w-[300px] bg-background border-r transform transition-transform duration-200 overflow-y-auto ${
            showAnalytics ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          {" "}
          <div className="p-4 md:p-6">
            <SearchAnalytics
              recentSearches={searchAnalytics}
              onSearchSelect={onAnalyticSelect}
            />
          </div>
        </div>

        {/* Main Content */}
        <main
          className={`pt-[73px] transition-all duration-200 ${
            showAnalytics ? "pl-[300px]" : "pl-0"
          }`}
        >
          <div className="max-w-3xl mx-auto p-4 md:p-8">
            <h2 className="text-3xl font-light mb-6">
              {greeting}, {userName}
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
          </div>
        </main>
      </div>
    );
  }
}
