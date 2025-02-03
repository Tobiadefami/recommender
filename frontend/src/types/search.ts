// src/types/search.ts

export interface Review {
  source: string;
  product_name: string;
  url?: string;
  review_summary: string;
  pros: string[] | null;
  cons: string[] | null;
  sentiment: string;
  is_product_of_interest: boolean;
  post_id: string;
  detail_score: number;
  balanced_score: number;
  well_written_score: number;
  comments?: Comment[];
  star_rating: number;
}

export interface Comment {
  text: string;
  url: string;
}

export interface SimilarProducts {
  same_brand: string[];
  competitors: string[];
  similar_category: string[];
}

export interface ProductInformation {
  brand: string;
  category: string;
  tier: string;
  release_year: string;
  price_range: string;
  key_features: string[];
  confidence_score: string;
  verified: boolean;
}
export interface SearchResult {
  reviews: Review[];
  overall_decision: string;
  similar_products: SimilarProducts;
  product_information?: ProductInformation;
}

export interface ComparisonView {
  mainProduct: SearchResult;
  comparedProducts: SearchResult[];
}

export interface SearchAnalytic {
  query: string;
  timestamp: string;
  resultCount: number;
  averageRating: number;
  sentiment: "positive" | "negative" | "neutral";
}

export interface RecentSearch {
  query: string;
  timestamp: Date;
  resultCount: number;
  averageRating?: number;
}
