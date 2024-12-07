// recommender/frontend/src/components/ReviewCard.tsx
import React, { useState } from "react";
import { Review } from "@/types/search";
import {
  ThumbsUp,
  ThumbsDown,
  Meh,
  Star,
  ChevronUp,
  ChevronDown,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const getScoreColor = (score: number): string => {
  if (score <= 1) return "bg-red-500";
  if (score <= 2) return "bg-orange-500";
  if (score <= 3) return "bg-yellow-500";
  if (score <= 4) return "bg-lime-500";
  return "bg-green-500";
};

const ScoreBar: React.FC<{ score: number; label: string }> = ({
  score,
  label,
}) => {
  const percentage = (score / 10) * 100;
  const colorClass = getScoreColor(score);

  return (
    <div className="mb-2">
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm font-medium">{label}</span>
        <span className="text-sm font-medium">{score.toFixed(1)}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
        <div
          className={`${colorClass} h-2.5 rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

const SentimentIcon: React.FC<{ sentiment: string }> = ({ sentiment }) => {
  switch (sentiment.toLowerCase()) {
    case "positive":
      return <ThumbsUp className="inline-block text-green-500" />;
    case "negative":
      return <ThumbsDown className="inline-block text-red-500" />;
    case "neutral":
      return <Meh className="inline-block text-yellow-500" />;
    default:
      return null;
  }
};

const StarRating: React.FC<{ rating: number }> = ({ rating }) => {
  return (
    <div className="flex items-center">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={`w-4 h-4 ${
            star <= rating ? "text-yellow-400 fill-current" : "text-gray-300"
          }`}
        />
      ))}
    </div>
  );
};

const ReviewCard: React.FC<{ review: Review }> = ({ review }) => {
  const [expanded, setExpanded] = useState(false);
  return (
    <div
      className={`bg-card shadow-md rounded-lg p-6 mb-4 transition-all duration-500 ease-in-out ${
        expanded ? "max-h-[1000px]" : "max-h-[300px]"
      } overflow-hidden`}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-xl font-semibold mb-2">{review.product_name}</h3>
        <StarRating rating={review.star_rating} />
      </div>
      <p className="text-sm text-muted-foreground mb-3">
        Source:{" "}
        {review.url ? (
          <a
            href={review.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
            {review.source}
          </a>
        ) : (
          review.source
        )}
      </p>
      <p className="mb-4">{review.review_summary}</p>

      {expanded && (
        <div className="transition-opacity duration-500 ease-in-out opacity-100">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <h4 className="font-semibold mb-2">Pros</h4>
              <ul className="list-disc list-inside">
                {review.pros &&
                  Array.isArray(review.pros) &&
                  review.pros.map((pro, index) => (
                    <li key={index} className="text-sm">
                      {pro}
                    </li>
                  ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Cons</h4>
              <ul className="list-disc list-inside">
                {review.cons &&
                  Array.isArray(review.cons) &&
                  review.cons.map((con, index) => (
                    <li key={index} className="text-sm">
                      {con}
                    </li>
                  ))}
              </ul>
            </div>
          </div>

          <div className="mt-4">
            <ScoreBar score={review.detail_score} label="Detail Score" />
            <ScoreBar score={review.balanced_score} label="Balanced Score" />
            <ScoreBar
              score={review.well_written_score}
              label="Well Written Score"
            />
          </div>
        </div>
      )}
      <div className="mt-4 text-sm flex justify-between items-center">
        <p>
          <span className="font-semibold">Sentiment:</span>{" "}
          {review.sentiment && <SentimentIcon sentiment={review.sentiment} />}
        </p>
        <Button
          onClick={() => setExpanded(!expanded)}
          variant="outline"
          size="sm"
          className="flex items-center gap-1"
        >
          {expanded ? (
            <>
              View Less <ChevronUp className="w-4 h-4" />
            </>
          ) : (
            <>
              View More <ChevronDown className="w-4 h-4" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

export default ReviewCard;

/* Changes made:
1. Added a transition animation to the review card's height using Tailwind classes `transition-all duration-500 ease-in-out` for a smooth expand/collapse effect when "View More" is clicked.
2. Wrapped the expandable content with a `transition-opacity` for a smooth fade-in effect.
3. Limited the height using `max-h` to prevent the card from taking up too much space when collapsed.
4. Used `overflow-hidden` to ensure that content outside the card is hidden during the animation.
*/
