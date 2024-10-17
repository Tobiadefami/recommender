// src/types/search.ts

export interface Review {
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

export interface SearchResult {
  reviews: Review[];
  overall_decision: string;
}