// recommender/frontend/src/components/SearchResults.tsx
import React from "react";
import { SearchResult, Review } from "@/types/search";

interface SearchResultsProps {
  results: SearchResult;
}

const ReviewCard: React.FC<{ review: Review }> = ({ review }) => (
  <div className="bg-card shadow-md rounded-lg p-6 mb-4">
    <h3 className="text-xl font-semibold mb-2">{review.product_name}</h3>
    <p className="text-sm text-muted-foreground mb-3">
      Source: {review.source}
    </p>
    <p className="mb-4">{review.review_summary}</p>

    <div className="grid grid-cols-2 gap-4 mb-4">
      <div>
        <h4 className="font-semibold mb-2">Pros</h4>
        <ul className="list-disc list-inside">
          {review.pros?.map((pro, index) => (
            <li key={index} className="text-sm">
              {pro}
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h4 className="font-semibold mb-2">Cons</h4>
        <ul className="list-disc list-inside">
          {review.cons?.map((con, index) => (
            <li key={index} className="text-sm">
              {con}
            </li>
          ))}
        </ul>
      </div>
    </div>

    <div className="grid grid-cols-2 gap-4 text-sm">
      <p>
        <span className="font-semibold">Sentiment:</span> {review.sentiment}
      </p>
      <p>
        <span className="font-semibold">Detail Score:</span>{" "}
        {review.detail_score}
      </p>
      <p>
        <span className="font-semibold">Balanced Score:</span>{" "}
        {review.balanced_score}
      </p>
      <p>
        <span className="font-semibold">Well Written Score:</span>{" "}
        {review.well_written_score}
      </p>
    </div>
  </div>
);

const SearchResults: React.FC<SearchResultsProps> = ({ results }) => {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Search Results</h2>
      <div className="bg-card shadow-md rounded-lg p-6 mb-6">
        <h3 className="text-xl font-semibold mb-2">Overall Decision</h3>
        <p>{results.overall_decision}</p>
      </div>
      <h3 className="text-xl font-semibold mb-4">Reviews</h3>
      {results.reviews.map((review, index) => (
        <ReviewCard key={index} review={review} />
      ))}
    </div>
  );
};

export default SearchResults;
