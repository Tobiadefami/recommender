// recommender/frontend/src/components/Autocomplete.tsx
import React, { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import api from "@/app/api";

interface AutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSuggestionSelect: (suggestion: string) => void;
}

export default function Autocomplete({
  value,
  onChange,
  onSuggestionSelect,
}: AutocompleteProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);

  useEffect(() => {
    if (value.length > 1) {
      fetchSuggestions();
    } else {
      setSuggestions([]);
    }
  }, [value]);

  const fetchSuggestions = async () => {
    try {
      const response = await api.get(
        `/autocomplete?query=${encodeURIComponent(value)}`,
      );
      setSuggestions(response.data);
    } catch (error) {
      console.error("Failed to fetch suggestions:", error);
    }
  };

  return (
    <div className="relative">
      <Input
        className="bg-transparent border-none text-lg placeholder-muted-foreground mb-4"
        placeholder="Iphone 16 pro max"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {suggestions.length > 0 && (
        <ul className="absolute w-full bg-background border border-input rounded-md mt-1">
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              className="px-4 py-2 hover:bg-accent cursor-pointer"
              onClick={() => onSuggestionSelect(suggestion)}
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
