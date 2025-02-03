import React from "react";
import { X } from "lucide-react";
import { Button } from "./ui/button";
import { SearchResult } from "@/types/search";
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
  return (
    <div
      className={`fixed top-0 right-0 h-full w-[600px] bg-background border-l shadow-xl transform transition-transform duration-200 overflow-y-auto z-50 ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="sticky top-0 bg-background p-4 border-b flex justify-between items-center">
        <h2 className="text-xl font-semibold">Product Analysis</h2>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="p-6">
        {isLoading ? (
          <LoadingCard />
        ) : (
          product && (
            <>
              {/* Product Information */}
              {product.product_information && (
                <div className="mb-8">
                  <h3 className="text-lg font-semibold mb-4">
                    Product Details
                  </h3>
                  <div className="space-y-2">
                    <p>
                      <span className="font-medium">Brand:</span>{" "}
                      {product.product_information.brand}
                    </p>
                    <p>
                      <span className="font-medium">Category:</span>{" "}
                      {product.product_information.category}
                    </p>
                    <p>
                      <span className="font-medium">Price Range:</span>{" "}
                      {product.product_information.price_range}
                    </p>
                    <p>
                      <span className="font-medium">Release Year:</span>{" "}
                      {product.product_information.release_year}
                    </p>
                    <div className="mt-4">
                      <p className="font-medium">Key Features:</p>
                      <ul className="list-disc pl-5 mt-2">
                        {product.product_information.key_features.map(
                          (feature, idx) => (
                            <li key={idx}>{feature}</li>
                          ),
                        )}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* Similar Products */}
              {product.similar_products && (
                <div className="mb-8">
                  <h3 className="text-lg font-semibold mb-4">
                    Similar Products
                  </h3>

                  {/* Same Brand Products */}
                  {product.similar_products.same_brand.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Same Brand</h4>
                      <div className="space-y-2">
                        {product.similar_products.same_brand.map(
                          (product, idx) => (
                            <div key={idx} className="p-4 bg-card rounded-lg">
                              <p>{product}</p>
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                  )}

                  {/* Competitors */}
                  {product.similar_products.competitors.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Competitors</h4>
                      <div className="space-y-2">
                        {product.similar_products.competitors.map(
                          (product, idx) => (
                            <div key={idx} className="p-4 bg-card rounded-lg">
                              <p>{product}</p>
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                  )}

                  {/* Similar Category */}
                  {product.similar_products.similar_category.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Similar Category</h4>
                      <div className="space-y-2">
                        {product.similar_products.similar_category.map(
                          (product, idx) => (
                            <div key={idx} className="p-4 bg-card rounded-lg">
                              <p>{product}</p>
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Overall Decision */}
              <div className="mt-8 p-4 bg-card rounded-lg">
                <h3 className="text-lg font-semibold mb-2">Overall Decision</h3>
                <p>{product.overall_decision}</p>
              </div>
            </>
          )
        )}
      </div>
    </div>
  );
};

export default SlideOutPanel;
