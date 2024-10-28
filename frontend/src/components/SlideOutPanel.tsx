import React, { useEffect } from "react";
import { X } from "lucide-react";
import { Button } from "./ui/button";
import { SearchResult } from "@/types/search";
import ReviewCard from "./ReviewCard";
import LoadingCard from "./LoadingCard";

interface SlideOutPanelProps {
  product: SearchResult | null;
  isOpen: boolean;
  onClose: () => void;
  isLoading: boolean;
}

const SlideOutPanel: React.FC<SlideOutPanelProps> = ({
  product,
  isOpen,
  onClose,
  isLoading,
}) => {
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscapeKey);
    }

    return () => {
      document.removeEventListener("keydown", handleEscapeKey);
    };
  }, [isOpen, onClose]);

  return (
    <div
      className={`fixed top-0 right-0 h-full w-[600px] bg-background border-l shadow-xl transform transition-transform duration-200 overflow-y-auto z-50 ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="sticky top-0 bg-background p-4 border-b flex justify-between items-center">
        <h2 className="text-xl font-semibold">Comparison Product</h2>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="hover:bg-accent hover:text-accent-foreground"
        >
          <X className="h-5 w-5 text-foreground" />
        </Button>
      </div>
      <div className="p-6">
        {isLoading ? (
          <>
            <h2 className="text-xl font-semibold mb-4">
              Loading comparison...
            </h2>
            <LoadingCard />
            <LoadingCard />
          </>
        ) : (
          product && (
            <>
              <div className="bg-card shadow-md rounded-lg p-6 mb-6">
                <h3 className="text-xl font-semibold mb-2">Overall Decision</h3>
                <p>{product.overall_decision}</p>
              </div>
              <h3 className="text-xl font-semibold mb-4">Reviews</h3>
              {product.reviews.map((review, index) => (
                <ReviewCard key={index} review={review} />
              ))}
            </>
          )
        )}
      </div>
    </div>
  );
};

export default SlideOutPanel;
