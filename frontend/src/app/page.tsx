// recommender/frontend/src/app/page.tsx
"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import SearchInterface from "@/components/SearchInterface";
import api from "./api";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/results?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  // const handleSearch = async (query: string) => {
  //   console.log("Searching for:", query);
  //   try {
  //     const response = await api.get(`/search/${encodeURIComponent(query)}`);
  //     console.log("Search results:", response.data);
  //     // Handle the search results here (e.g., update state, navigate to results page)
  //   } catch (error) {
  //     console.error("Failed to search:", error);
  //   }
  // };

  const handleSuggestionSelect = (suggestion: string) => {
    setSearchQuery(suggestion);
    router.push(`/results?q=${encodeURIComponent(suggestion)}`);
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
      onSearchQueryChange={setSearchQuery}
      onSubmit={handleSubmit}
      onSuggestionSelect={handleSuggestionSelect}
      recentSearches={recentSearches}
      onViewAllSearches={() => console.log("View all searches")}
      onClearSuggestions={() => console.log("Clear suggestions")}
    />
  );
}
