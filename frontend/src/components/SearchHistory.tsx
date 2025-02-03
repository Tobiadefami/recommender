import React from "react";
import { SearchAnalytic } from "@/types/search";
import { formatDistanceToNow } from "date-fns";
import { Button } from "./ui/button";
import { Search } from "lucide-react";

interface SearchHistoryProps {
  history: SearchAnalytic[];
  onSearchSelect: (query: string) => void;
  isLoading: boolean;
}

export default function SearchHistory({
  history,
  onSearchSelect,
  isLoading,
}: SearchHistoryProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse bg-muted h-12 rounded-lg" />
        <div className="animate-pulse bg-muted h-12 rounded-lg" />
        <div className="animate-pulse bg-muted h-12 rounded-lg" />
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No search history yet
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {history.map((item, index) => (
        <div
          key={index}
          className="bg-card/50 backdrop-blur-sm rounded-lg p-4 shadow-sm
                     border border-border/50 hover:border-border transition-colors"
        >
          <div className="flex justify-between items-center">
            <div className="flex-1">
              <p className="font-medium truncate">{item.query}</p>
              <p className="text-sm text-muted-foreground">
                {formatDistanceToNow(new Date(item.timestamp), {
                  addSuffix: true,
                })}
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.preventDefault();
                onSearchSelect(item.query);
              }}
              className="ml-2"
            >
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
