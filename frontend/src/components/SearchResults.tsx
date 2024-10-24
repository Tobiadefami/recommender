// recommender/frontend/src/components/SearchResults.tsx
import React, { useState } from "react";
import { SearchResult } from "@/types/search";
import { Button } from "@/components/ui/button";
import api from "@/app/api";
import ReviewCard from "./ReviewCard";
import SlideOutPanel from "./SlideOutPanel";

interface SearchResultsProps {
  results: SearchResult;
}

// recommender/frontend/src/components/SearchResults.tsx
const SearchResults: React.FC<SearchResultsProps> = ({ results }) => {
  const [comparisonProduct, setComparisonProduct] =
    useState<SearchResult | null>(null);
  const [isLoadingComparison, setIsLoadingComparison] = useState(false);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  const handleCompareProduct = async (productName: string) => {
    setIsLoadingComparison(true);
    setIsPanelOpen(true);
    // Clear the previous comparison while loading
    setComparisonProduct(null);

    try {
      const [response, similarResponse] = await Promise.all([
        api.get(`/search/${encodeURIComponent(productName)}`),
        api.get(`/similar_products/${encodeURIComponent(productName)}`),
      ]);

      setComparisonProduct({
        ...response.data,
        similar_products: similarResponse.data.similar_products,
      });
    } catch (error) {
      console.error("Failed to fetch comparison product:", error);
      // Optionally show an error message to the user
    } finally {
      setIsLoadingComparison(false);
    }
  };

  const handleClosePanel = () => {
    setIsPanelOpen(false);
    // Optional: Clear the comparison product after animation completes
    setTimeout(() => {
      setComparisonProduct(null);
    }, 200); // Match the duration of the slide-out animation
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Search Results</h2>
      <div className="bg-card shadow-md rounded-lg p-6 mb-6">
        <h3 className="text-xl font-semibold mb-2">Overall Decision</h3>
        <p>{results.overall_decision}</p>
      </div>

      {results.similar_products && results.similar_products.length > 0 && (
        <div className="bg-card shadow-md rounded-lg p-6 mb-6">
          <h3 className="text-xl font-semibold mb-4">Similar Products</h3>
          <div className="flex flex-wrap gap-2">
            {results.similar_products.map((product, index) => (
              <Button
                key={index}
                variant="secondary"
                size="sm"
                onClick={() => handleCompareProduct(product)}
                className="rounded-full"
              >
                {product}
              </Button>
            ))}
          </div>
        </div>
      )}

      <h3 className="text-xl font-semibold mb-4">Reviews</h3>
      {results.reviews.map((review, index) => (
        <ReviewCard key={index} review={review} />
      ))}

      <SlideOutPanel
        product={comparisonProduct}
        isOpen={isPanelOpen}
        onClose={handleClosePanel}
        isLoading={isLoadingComparison}
      />
    </div>
  );
};

export default SearchResults;
