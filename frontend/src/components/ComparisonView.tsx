import React from "react";
import { ComparisonView as ComparisonViewType } from "@/types/search";
import SearchResults from "./SearchResults";

interface ComparisonViewProps {
  comparisonView: ComparisonViewType;
  onCompareProduct: (productName: string) => void;
}

const ComparisonView: React.FC<ComparisonViewProps> = ({
  comparisonView,
  onCompareProduct,
}) => {
  const { mainProduct, comparedProducts } = comparisonView;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div className="col-span-1">
        <SearchResults
          results={mainProduct}
          isMainProduct={true}
          onCompareProduct={onCompareProduct}
        />
      </div>
      {comparedProducts.map((product, index) => (
        <div key={index} className="col-span-1">
          <SearchResults results={product} isMainProduct={false} />
        </div>
      ))}
    </div>
  );
};

export default ComparisonView;
