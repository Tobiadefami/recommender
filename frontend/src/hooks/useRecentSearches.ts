import { useState, useEffect } from "react";
import { RecentSearch } from "@/types/search";

const RECENT_SEARCHES_KEY = "recent_searches";
const MAX_RECENT_SEARCHES = 10;

type StoredSearch = Omit<RecentSearch, "timestamp"> & { timestamp: string };

export function useRecentSearches() {
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);

  // Load searches from localStorage on mount
  useEffect(() => {
    const savedSearches = localStorage.getItem(RECENT_SEARCHES_KEY);
    if (savedSearches) {
      const parsedSearches = JSON.parse(savedSearches) as StoredSearch[];
      // Convert string dates back to Date objects
      const searchesWithDates = parsedSearches.map((search) => ({
        ...search,
        timestamp: new Date(search.timestamp),
      }));
      setRecentSearches(searchesWithDates);
    }
  }, []);

  const addRecentSearch = (
    query: string,
    resultCount: number,
    averageRating?: number,
  ) => {
    const newSearch: RecentSearch = {
      query,
      timestamp: new Date(),
      resultCount,
      averageRating,
    };

    setRecentSearches((prevSearches) => {
      // Remove duplicate if exists
      const filteredSearches = prevSearches.filter(
        (search) => search.query.toLowerCase() !== query.toLowerCase(),
      );

      // Add new search to beginning and limit to MAX_RECENT_SEARCHES
      const updatedSearches = [newSearch, ...filteredSearches].slice(
        0,
        MAX_RECENT_SEARCHES,
      );

      // Save to localStorage
      localStorage.setItem(
        RECENT_SEARCHES_KEY,
        JSON.stringify(updatedSearches),
      );

      return updatedSearches;
    });
  };

  const clearRecentSearches = () => {
    localStorage.removeItem(RECENT_SEARCHES_KEY);
    setRecentSearches([]);
  };

  const removeRecentSearch = (query: string) => {
    setRecentSearches((prevSearches) => {
      const updatedSearches = prevSearches.filter(
        (search) => search.query.toLowerCase() !== query.toLowerCase(),
      );
      localStorage.setItem(
        RECENT_SEARCHES_KEY,
        JSON.stringify(updatedSearches),
      );
      return updatedSearches;
    });
  };

  return {
    recentSearches,
    addRecentSearch,
    clearRecentSearches,
    removeRecentSearch,
  };
}
