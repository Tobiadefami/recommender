"use client";

import SearchInterface from "@/components/SearchInterface";
// import api from "./api";

export default function Home() {
  const handleSearch = (query: string) => {
    // Implement search logic
    console.log("Searching for:", query);
  };

  const recentSearches = [
    { title: "Product Review Search Interface", daysAgo: 2 },
    { title: "Company Registration Number Inquiry", daysAgo: 3 },
    { title: "Percentage Difference Between 1.72 and 3.50...", daysAgo: 4 },
  ];

  // const fetchRecentChats = async () => {
  //   try {
  //     const response = await api.get("/recent-chats");
  //     console.log("Recent chats:", response.data);
  //   } catch (error) {
  //     console.error("Failed to fetch recent chats:", error);
  //   }
  // };
  return (
    <SearchInterface
      userName="John"
      onSearch={handleSearch}
      recentSearches={recentSearches}
      onViewAllSearches={() => console.log("View all searches")}
      onClearSuggestions={() => console.log("Clear suggestions")}
    />
  );
}
