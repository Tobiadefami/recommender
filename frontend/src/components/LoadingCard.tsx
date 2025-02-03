// recommender/frontend/src/components/LoadingCard.tsx
import React from "react";

const LoadingCard: React.FC = () => {
  return (
    <div className="bg-card shadow-md rounded-lg p-6 w-full mb-4 animate-pulse">
      <div className="h-4 bg-gray-300 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-gray-300 rounded w-1/2 mb-4"></div>
      <div className="h-4 bg-gray-300 rounded w-5/6 mb-4"></div>
      <div className="h-4 bg-gray-300 rounded w-2/3 mb-4"></div>
      <div className="grid grid-cols-2 gap-4 mt-6">
        <div className="h-4 bg-gray-300 rounded"></div>
        <div className="h-4 bg-gray-300 rounded"></div>
      </div>
    </div>
  );
};

export default LoadingCard;
