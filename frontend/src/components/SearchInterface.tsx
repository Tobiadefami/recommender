import React, { useState, useEffect } from "react";
import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./ThemeToggle";
import UserMenu from "./UserMenu";
import Autocomplete from "./Autocomplete";
import getGreeting from "@/lib/greeting";
import { SearchResult, SearchAnalytic } from "@/types/search";
import SearchResults from "./SearchResults";
import LoadingCard from "./LoadingCard";
import SearchHistory from "./SearchHistory";
import { formatDistanceToNow } from "date-fns";
import RedditConnectBanner from "./RedditConnectBanner";

interface SearchInterfaceProps {
  username: string;
  searchQuery: string;
  onSearchQueryChange: (query: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onSuggestionSelect: (suggestion: string) => void;
  onClearSuggestions: () => void;
  onLogout: () => void;
  results: SearchResult | null;
  loading: boolean;
  showSuggestions: boolean;
  recentSearches: SearchAnalytic[];
  allSearchHistory: SearchAnalytic[];
  isLoadingHistory: boolean;
  hasRedditConnection: boolean;
  showRedditBanner: boolean;
  onRedditConnect: () => void;
  onRedditBannerDismiss: () => void;
}

export default function SearchInterface({
  username,
  searchQuery,
  onSearchQueryChange,
  onSubmit,
  onSuggestionSelect,
  onClearSuggestions,
  onLogout,
  results,
  loading,
  showSuggestions,
  recentSearches,
  allSearchHistory,
  isLoadingHistory,
  hasRedditConnection,
  showRedditBanner,
  onRedditConnect,
  onRedditBannerDismiss,
}: SearchInterfaceProps) {
  const [greeting, setGreeting] = useState<string>("");
  const [showAnalytics, setShowAnalytics] = useState<boolean>(false);

  useEffect(() => {
    setGreeting(getGreeting(new Date()));
  }, []);

  const SearchForm = () => (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(e);
      }}
      className="bg-card/50 backdrop-blur-sm rounded-3xl p-6 shadow-lg
                border border-border/50 hover:border-border transition-colors"
    >
      <div className="relative">
        <Search className="absolute w-5 h-5 left-3 top-1/2 transform -translate-y-1/2 text-gray-400 md:w-6 md:h-6" />
        <Autocomplete
          value={searchQuery}
          onChange={onSearchQueryChange}
          onSuggestionSelect={onSuggestionSelect}
          onSubmit={onSubmit}
          showSuggestions={showSuggestions}
        />
      </div>
      {!results && (
        <>
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
        </>
      )}
    </form>
  );

  // Calculate header height based on whether results are present
  const headerHeight = results ? "header-with-search" : "header-without-search";

  return (
    <div className="min-h-screen flex flex-col font-roboto bg-background text-foreground">
      {/* Fixed header */}
      <header
        className={`fixed top-0 left-0 right-0 bg-background/95 backdrop-blur-sm z-40 p-4 md:p-8 border-b ${results ? "pb-8" : ""}`}
      >
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <a href="/">
              <h1 className="text-2xl md:text-3xl font-semibold">Recommendr</h1>
            </a>
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
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <UserMenu username={username} onLogout={onLogout} />
          </div>
        </div>

        {/* Fixed search bar when results are present */}
        {results && (
          <div className="mt-6 max-w-2xl mx-auto">
            <SearchForm />
          </div>
        )}
      </header>

      {/* Slide-out Analytics Panel */}
      <div
        className={`fixed top-[${headerHeight}] left-0 h-[calc(100vh-${headerHeight})] w-[300px] bg-background border-r transform transition-transform duration-200 ${
          showAnalytics ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="p-4 md:p-6">
          <SearchHistory
            history={allSearchHistory}
            onSearchSelect={onSuggestionSelect}
            isLoading={isLoadingHistory}
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
          {/* Adjust top margin based on whether results are present */}
          <div
            className={`${results ? "mt-[200px]" : "mt-[180px]"} md:${results ? "mt-[220px]" : "mt-[200px]"} flex flex-col items-center`}
          >
            {showRedditBanner && !hasRedditConnection && (
              <div className="w-full max-w-2xl mb-6">
                <RedditConnectBanner
                  onDismiss={onRedditBannerDismiss}
                  onConnect={onRedditConnect}
                />
              </div>
            )}

            {!results && !loading ? (
              <>
                <h2 className="text-3xl md:text-4xl font-light mb-12 text-center">
                  {greeting}, {username}
                </h2>

                <div className="w-full max-w-2xl mt-16">
                  <SearchForm />

                  {/* Recent Searches */}
                  {recentSearches.length > 0 && (
                    <div className="w-full mt-12">
                      <div className="mb-4 flex justify-between items-center">
                        <h3 className="text-sm font-semibold flex items-center gap-2">
                          <Search className="w-4 h-4" />
                          Recent Searches
                        </h3>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowAnalytics(true)}
                          className="text-muted-foreground"
                        >
                          View all
                        </Button>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {recentSearches.map((search, index) => (
                          <div
                            key={index}
                            className="bg-card p-4 rounded-lg cursor-pointer hover:bg-accent/50 transition-colors"
                            onClick={() => onSuggestionSelect(search.query)}
                          >
                            <h4 className="font-medium mb-2">{search.query}</h4>
                            <div className="flex flex-col gap-1 text-sm text-muted-foreground">
                              <span>
                                {formatDistanceToNow(
                                  new Date(search.timestamp),
                                  {
                                    addSuffix: true,
                                  },
                                )}
                              </span>
                              <div className="flex items-center gap-2">
                                <span>{search.resultCount} results</span>
                                <span>•</span>
                                <span>
                                  Rating: {search.averageRating.toFixed(1)}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="w-full max-w-2xl">
                {/* Loading State */}
                {loading && (
                  <div>
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
