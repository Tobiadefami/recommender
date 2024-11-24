"use client";

import React, { useEffect, useState } from "react";
import { SearchAnalytic, SearchResult } from "@/types/search";

import Login from "@/components/Login";
import SearchInterface from "@/components/SearchInterface";
import api from "@/app/api";
import { useCallback } from "react";

export default function Home() {
  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);

  // User and authentication state
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [username, setUsername] = useState("");

  // Search history state
  const [allSearchHistory, setAllSearchHistory] = useState<SearchAnalytic[]>(
    [],
  );
  const [recentSearches, setRecentSearches] = useState<SearchAnalytic[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  // Reddit Connection
  const [hasRedditConnection, setHasRedditConnection] = useState(false);
  const [showRedditBanner, setShowRedditBanner] = useState(true);

  const handleLogout = useCallback(() => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    setUsername("");
    setAllSearchHistory([]);
    setRecentSearches([]);
    setResults(null);
    setSearchQuery("");
  }, []);

  // Fetch search history when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchSearchHistory();
    }
  }, [isAuthenticated]);

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const response = await api.get("/users/me");
        setUsername(response.data.username);
        setHasRedditConnection(response.data.has_reddit_refresh_token);
        setIsAuthenticated(true);
      } catch (error) {
        console.log(error);
        handleLogout();
      }
    } else {
      setIsAuthenticated(false);
    }
  }, [handleLogout]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const handleRedditConnect = async () => {
    try {
      const response = await api.get<{ url: string }>("/reddit/auth");
      window.location.href = response.data.url;
    } catch (error) {
      console.error("Failed to connect to Reddit:", error);
    }
  };

  const handleRedditBannerDismiss = () => {
    setShowRedditBanner(false);
  };

  // Update the banner visibility when Reddit connection status changes
  useEffect(() => {
    if (hasRedditConnection) {
      setShowRedditBanner(false);
    }
  }, [hasRedditConnection]);

  const handleAuthSuccess = () => {
    checkAuth(); // Re-check auth to get username
  };

  const fetchSearchHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const response = await api.get<SearchAnalytic[]>(
        "/user/search-analytics",
      );
      const sortedHistory = response.data.sort(
        (a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
      );
      setAllSearchHistory(sortedHistory);
      setRecentSearches(sortedHistory.slice(0, 3)); // Get most recent 3 searches
    } catch (error) {
      console.error("Failed to fetch search history:", error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const fetchResults = async (query: string) => {
    setLoading(true);
    setResults(null);
    try {
      const [searchResponse, similarProductsResponse] = await Promise.all([
        api.get(`/search/${encodeURIComponent(query)}`),
        api.get(`/similar_products/${encodeURIComponent(query)}`),
      ]);

      setResults({
        ...searchResponse.data,
        similar_products: similarProductsResponse.data.similar_products || {
          same_brand: [],
          competitors: [],
          similar_category: [],
        },
      });

      // Refresh search history after successful search
      await fetchSearchHistory();
    } catch (error) {
      console.error("Failed to fetch search results:", error);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setShowSuggestions(false);
      await fetchResults(searchQuery);
    }
  };

  const handleSuggestionSelect = async (suggestion: string) => {
    setSearchQuery(suggestion);
    setShowSuggestions(false);
    await fetchResults(suggestion);
  };

  const handleSearchQueryChange = (query: string) => {
    setSearchQuery(query);
    setShowSuggestions(true);
  };

  const handleClearSuggestions = () => {
    setSearchQuery("");
    setResults(null);
    setShowSuggestions(true);
  };

  // Show loading state while checking authentication
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <Login onAuthSuccess={handleAuthSuccess} />;
  }

  // Main application
  return (
    <SearchInterface
      username={username}
      searchQuery={searchQuery}
      onSearchQueryChange={handleSearchQueryChange}
      onSubmit={handleSubmit}
      onSuggestionSelect={handleSuggestionSelect}
      onClearSuggestions={handleClearSuggestions}
      onLogout={handleLogout}
      onRedditConnect={handleRedditConnect}
      onRedditBannerDismiss={handleRedditBannerDismiss}
      results={results}
      loading={loading}
      showSuggestions={showSuggestions}
      recentSearches={recentSearches}
      allSearchHistory={allSearchHistory}
      isLoadingHistory={isLoadingHistory}
      hasRedditConnection={hasRedditConnection}
      showRedditBanner={showRedditBanner}
    />
  );
}
