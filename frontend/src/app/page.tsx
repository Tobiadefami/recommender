"use client";
import React, { useState } from "react";
import SearchInterface from "@/components/SearchInterface";
import api from "@/app/api";
import { SearchResult } from "@/types/search";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);

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

  const fetchResults = async (query: string) => {
    setLoading(true);
    try {
      const response = await api.get(`/search/${encodeURIComponent(query)}`);
      setResults(response.data);
    } catch (error) {
      console.error("Failed to fetch search results:", error);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchQueryChange = (query: string) => {
    setSearchQuery(query);
    setShowSuggestions(true);
  };

  const recentSearches = [
    { title: "Product Review Search Interface", daysAgo: 2 },
    { title: "Company Registration Number Inquiry", daysAgo: 3 },
    { title: "Percentage Difference Between 1.72 and 3.50...", daysAgo: 4 },
  ];

  return (
    <SearchInterface
      userName="John"
      searchQuery={searchQuery}
      onSearchQueryChange={handleSearchQueryChange}
      onSubmit={handleSubmit}
      onSuggestionSelect={handleSuggestionSelect}
      recentSearches={recentSearches}
      onViewAllSearches={() => console.log("View all searches")}
      onClearSuggestions={() => {
        setSearchQuery("");
        setResults(null);
        setShowSuggestions(true);
      }}
      results={results}
      loading={loading}
      showSuggestions={showSuggestions}
    />
  );
}
