import React, { useState, useEffect } from "react";
import { Search, X, Menu } from "lucide-react";
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
import CategorySelector from "./Categories";

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
  onDirectSearch: (query: string) => Promise<void>;
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
  onDirectSearch,
}: SearchInterfaceProps) {
  const [greeting, setGreeting] = useState<string>("");
  const [showAnalytics, setShowAnalytics] = useState<boolean>(false);

  useEffect(() => {
    setGreeting(getGreeting(new Date()));
  }, []);

  // Pass in the prop "compact" so you can set smaller styling if results exist
  const SearchForm = ({ compact }: { compact?: boolean }) => (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(e);
      }}
      className={`
          bg-card/50
          backdrop-blur-sm
          rounded-3xl
          shadow-lg
          border
          border-border/50
          hover:border-border
          transition-colors
          ${compact ? "p-4" : "p-6"}
        `}
    >
      <div className="relative">
        <Autocomplete
          value={searchQuery}
          onChange={onSearchQueryChange}
          onSuggestionSelect={onSuggestionSelect}
          onSubmit={onSubmit}
          showSuggestions={showSuggestions}
          autoFocus={!results}
        />
      </div>
      {/* The rest of the form (example buttons) only show if !results */}
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
            {/* ...other example buttons... */}
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

  return (
    <div className="min-h-screen flex flex-col font-roboto bg-background text-foreground">
      {/* Fixed header */}
      <header
        className={`
          fixed top-0 left-0 right-0
          bg-background/95
          backdrop-blur-sm
          z-40
          p-4 md:p-6
          border-b
          flex items-center
          justify-between
          ${results ? "pb-2" : ""}
        `}
      >
        {/* Left side: App name + inline search bar */}
        <div className="flex items-center gap-2 w-full md:w-auto">
          <a href="/" className="flex items-center gap-2">
            <h1
              className={`
                font-semibold
                transition-all
                ${results ? "text-xl md:text-2xl" : "text-2xl md:text-3xl"}
              `}
            >
              Recommendr
            </h1>
          </a>

          {/* When results exist, show a smaller search bar inline */}
          {results && (
            <div className="flex-grow ml-4">
              <SearchForm compact />
            </div>
          )}
        </div>

        {/* Right side: Hamburger menu + Theme toggle + User menu */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAnalytics(!showAnalytics)}
            className="flex items-center gap-2"
          >
            <Menu className="w-4 h-4" />
          </Button>
          <ThemeToggle />
          <UserMenu username={username} onLogout={onLogout} />
        </div>
      </header>

      {/* OPTIONAL: Dark overlay for analytics */}
      {showAnalytics && (
        <div
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-[5] transition-all duration-200 ease-in-out"
          onClick={() => setShowAnalytics(false)}
        />
      )}

      {/* Slide-out Analytics Panel */}
      <div
        className={`
          fixed
          top-[72px]
          left-0
          h-[calc(100vh-72px)]
          w-[300px]
          bg-background
          border-r
          transform
          transition-transform
          duration-200
          z-10
          ${showAnalytics ? "translate-x-0" : "-translate-x-full"}
        `}
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
      <main className="mt-20">
        <div
          className={`
            ${results || loading ? "ml-8" : "mx-auto"}
            max-w-3xl
            p-4
            md:p-8
          `}
        >
          <div
            className={`
              ${results ? "mt-[150px]" : "mt-[180px]"}
              md:${results ? "mt-[170px]" : "mt-[200px]"}
              flex flex-col
            `}
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
                  {/* Use a non-compact search bar when no results */}
                  <SearchForm />
                  <div className="w-full max-w-2xl mb-8">
                    <CategorySelector
                      onCategorySelect={(product) => {
                        onDirectSearch(product);
                      }}
                    />
                  </div>
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
                {loading && (
                  <div className="w-full">
                    <LoadingCard />
                    <LoadingCard />
                    <LoadingCard />
                  </div>
                )}

                {results && <SearchResults results={results} />}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
