import React from "react";
import { SearchAnalytic } from "@/types/search";
import { ThumbsUp, ThumbsDown, Meh, Clock, BarChart2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface SearchAnalyticsProps {
  recentSearches: SearchAnalytic[];
  onSearchSelect: (query: string) => void;
}

const getSentimentIcon = (sentiment: string) => {
  switch (sentiment) {
    case "positive":
      return <ThumbsUp className="w-4 h-4 text-green-500" />;
    case "negative":
      return <ThumbsDown className="w-4 h-4 text-red-500" />;
    default:
      return <Meh className="w-4 h-4 text-yellow-500" />;
  }
};

const SearchAnalytics: React.FC<SearchAnalyticsProps> = ({
  recentSearches,
  onSearchSelect,
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <BarChart2 className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Search Analytics</h3>
      </div>

      <div className="space-y-3">
        {recentSearches.map((search, index) => (
          <div
            key={index}
            className="bg-card p-3 rounded-lg hover:bg-accent cursor-pointer transition-colors"
            onClick={() => onSearchSelect(search.query)}
          >
            <p className="font-medium truncate">{search.query}</p>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
              <Clock className="w-4 h-4" />
              <span>
                {formatDistanceToNow(search.timestamp, { addSuffix: true })}
              </span>
            </div>
            <div className="flex items-center justify-between mt-2">
              <span className="text-sm text-muted-foreground">
                {search.resultCount} results
              </span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">
                  {search.averageRating.toFixed(1)}
                </span>
                {getSentimentIcon(search.sentiment)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchAnalytics;
