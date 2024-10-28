"use client";
import React, { useState } from "react";
import SearchInterface from "@/components/SearchInterface";
import api from "@/app/api";
import { SearchResult, SearchAnalytic } from "@/types/search";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);

  const fetchResults = async (query: string) => {
    setLoading(true);
    try {
      const [searchResponse, similarProductsResponse] = await Promise.all([
        api.get(`/search/${encodeURIComponent(query)}`),
        api.get(`/similar_products/${encodeURIComponent(query)}`),
      ]);

      setResults({
        ...searchResponse.data,
        similar_products: similarProductsResponse.data.similar_products,
      });
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

  const handleAnalyticSelect = (query: string) => {
    setSearchQuery(query);
    fetchResults(query);
  };

  const recentSearches = [
    { title: "Product Review Search Interface", daysAgo: 2 },
    { title: "Company Registration Number Inquiry", daysAgo: 3 },
    { title: "Percentage Difference Between 1.72 and 3.50...", daysAgo: 4 },
  ];

  const searchAnalytics: SearchAnalytic[] = [
    {
      query: "MacBook Pro M2",
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
      resultCount: 145,
      averageRating: 4.5,
      sentiment: "positive",
    },
    {
      query: "iPhone 15 Pro",
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
      resultCount: 230,
      averageRating: 4.2,
      sentiment: "positive",
    },
    {
      query: "Sony WH-1000XM5",
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5),
      resultCount: 89,
      averageRating: 3.8,
      sentiment: "neutral",
    },
    {
      query: "Samsung S24 Ultra",
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24),
      resultCount: 178,
      averageRating: 4.7,
      sentiment: "positive",
    },
    {
      query: "Pixel 8 Pro",
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48),
      resultCount: 156,
      averageRating: 3.2,
      sentiment: "negative",
    },
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
      onClearSuggestions={handleClearSuggestions}
      results={results}
      loading={loading}
      showSuggestions={showSuggestions}
      searchAnalytics={searchAnalytics}
      onAnalyticSelect={handleAnalyticSelect}
    />
  );
}
