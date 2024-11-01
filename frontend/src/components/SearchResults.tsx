import React, { useState } from "react";
import { SearchResult } from "@/types/search";
import { Button } from "@/components/ui/button";
import api from "@/app/api";
import ReviewCard from "./ReviewCard";
import SlideOutPanel from "./SlideOutPanel";
import { cn } from "@/lib/utils";

interface SearchResultsProps {
  results: SearchResult;
}

const SearchResults: React.FC<SearchResultsProps> = ({ results }) => {
  const [comparisonProduct, setComparisonProduct] =
    useState<SearchResult | null>(null);
  const [isLoadingComparison, setIsLoadingComparison] = useState(false);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  const handleCompareProduct = async (productName: string) => {
    setIsLoadingComparison(true);
    setIsPanelOpen(true);
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
    } finally {
      setIsLoadingComparison(false);
    }
  };

  const handleClosePanel = () => {
    setIsPanelOpen(false);
    setTimeout(() => {
      setComparisonProduct(null);
    }, 200);
  };

  const getSimilarProductButtonStyle = (category: string) => {
    switch (category) {
      case "Same Brand Products":
        return "bg-card hover:bg-accent text-blue-500 border-blue-200 dark:border-blue-800";
      case "Competitor Products":
        return "bg-card hover:bg-accent text-green-500 border-green-200 dark:border-green-800";
      case "Similar Category Products":
        return "bg-card hover:bg-accent text-purple-500 border-purple-200 dark:border-purple-800";
      default:
        return "bg-card hover:bg-accent";
    }
  };

  const renderSimilarProductsSection = (title: string, products: string[]) => {
    if (!products || products.length === 0) return null;

    const buttonStyle = getSimilarProductButtonStyle(title);

    return (
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-muted-foreground mb-2">
          {title}
        </h4>
        <div className="flex flex-wrap gap-2">
          {products.map((product, index) => (
            <Button
              key={index}
              variant="outline"
              size="sm"
              onClick={() => handleCompareProduct(product)}
              className={cn("rounded-full border", buttonStyle)}
            >
              {product}
            </Button>
          ))}
        </div>
      </div>
    );
  };

  const renderSimilarProductsCard = () => {
    if (!results.similar_products) return null;

    const hasSimilarProducts =
      (results.similar_products.same_brand &&
        results.similar_products.same_brand.length > 0) ||
      (results.similar_products.competitors &&
        results.similar_products.competitors.length > 0) ||
      (results.similar_products.similar_category &&
        results.similar_products.similar_category.length > 0);

    if (!hasSimilarProducts) return null;

    return (
      <div className="bg-card shadow-md rounded-lg p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">Similar Products</h3>
        {renderSimilarProductsSection(
          "Same Brand Products",
          results.similar_products.same_brand || [],
        )}
        {renderSimilarProductsSection(
          "Competitor Products",
          results.similar_products.competitors || [],
        )}
        {renderSimilarProductsSection(
          "Similar Category Products",
          results.similar_products.similar_category || [],
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Search Results</h2>

      {/* Overall Decision Card */}
      <div className="bg-card shadow-md rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-2">Overall Decision</h3>
        <p className="text-muted-foreground">{results.overall_decision}</p>
      </div>

      {/* Similar Products Section */}
      {renderSimilarProductsCard()}

      {/* Reviews Section */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Reviews</h3>
        <div className="space-y-4">
          {results.reviews.map((review, index) => (
            <ReviewCard key={index} review={review} />
          ))}
        </div>
      </div>

      {/* Comparison Panel */}
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
