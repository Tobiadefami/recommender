// recommender/frontend/src/app/Results.tsx
"use client";
import React from "react";
import { useSearchParams } from "next/navigation";
import api from "@/app/api";

interface Review {
  source: string;
  product_name: string;
  review_summary: string;
  pros: string[] | null;
  cons: string[] | null;
  sentiment: string;
  is_product_of_interest: boolean;
  post_id: string;
  detail_score: number;
  balanced_score: number;
  well_written_score: number;
}

interface SearchResult {
  reviews: Review[];
  overall_decision: string;
}

export default function ResultsPage() {
  const [results, setResults] = React.useState<SearchResult | null>(null);
  const [loading, setLoading] = React.useState(true);
  const searchParams = useSearchParams();
  const query = searchParams.get("q");

  React.useEffect(() => {
    if (query) {
      fetchResults(query);
    }
  }, [query]);

  const fetchResults = async (searchQuery: string) => {
    setLoading(true);
    try {
      const response = await api.get(
        `/search/${encodeURIComponent(searchQuery)}`,
      );
      setResults(response.data);
    } catch (error) {
      console.error("Failed to fetch search results:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!results) {
    return <div>No results found.</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Search Results for: {query}</h1>

      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Overall Decision</h2>
        <p className="text-lg">{results.overall_decision}</p>
      </div>

      <h2 className="text-2xl font-semibold mb-4">Reviews</h2>
      {results.reviews.map((review, index) => (
        <div key={index} className="mb-8 p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-2">{review.product_name}</h3>
          <p className="mb-2">
            <strong>Source:</strong> {review.source}
          </p>
          <p className="mb-4">{review.review_summary}</p>

          {review.pros && review.pros.length > 0 && (
            <div className="mb-2">
              <strong>Pros:</strong>
              <ul className="list-disc list-inside">
                {review.pros.map((pro, i) => (
                  <li key={i}>{pro}</li>
                ))}
              </ul>
            </div>
          )}

          {review.cons && review.cons.length > 0 && (
            <div className="mb-2">
              <strong>Cons:</strong>
              <ul className="list-disc list-inside">
                {review.cons.map((con, i) => (
                  <li key={i}>{con}</li>
                ))}
              </ul>
            </div>
          )}

          <p>
            <strong>Sentiment:</strong> {review.sentiment}
          </p>
          <p>
            <strong>Detail Score:</strong> {review.detail_score}
          </p>
          <p>
            <strong>Balanced Score:</strong> {review.balanced_score}
          </p>
          <p>
            <strong>Well Written Score:</strong> {review.well_written_score}
          </p>
        </div>
      ))}
    </div>
  );
}
