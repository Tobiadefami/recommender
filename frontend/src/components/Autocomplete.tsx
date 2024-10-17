// recommender/frontend/src/components/Autocomplete.tsx
import React, { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import api from "@/app/api";

interface AutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSuggestionSelect: (suggestion: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  showSuggestions: boolean;
}

export default function Autocomplete({
  value,
  onChange,
  onSuggestionSelect,
  onSubmit,
  showSuggestions,
}: AutocompleteProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const suggestionsRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    if (value.length > 1) {
      fetchSuggestions();
    } else {
      setSuggestions([]);
    }
  }, [value]);

  useEffect(() => {
    if (!showSuggestions) {
      setFocusedIndex(-1);
    }
  }, [showSuggestions]);

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

  const handleSuggestionClick = (suggestion: string) => {
    onSuggestionSelect(suggestion);
    setSuggestions([]); // Clear suggestions after selecting one
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (focusedIndex >= 0 && focusedIndex < suggestions.length) {
        onSuggestionSelect(suggestions[focusedIndex]);
      } else {
        onSubmit(e);
      }
      setSuggestions([]);
      setFocusedIndex(-1);
    } else if (e.key == "ArrowDown") {
      e.preventDefault();
      setFocusedIndex((prevIndex) =>
        prevIndex < suggestions.length - 1 ? prevIndex + 1 : prevIndex,
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setFocusedIndex((prevIndex) => (prevIndex > 0 ? prevIndex - 1 : -1));
    }
  };

  useEffect(() => {
    if (suggestionsRef.current && focusedIndex >= 0) {
      const focusedElement = suggestionsRef.current.children[
        focusedIndex
      ] as HTMLElement;
      focusedElement.scrollIntoView({ block: "nearest" });
    }
  }, [focusedIndex]);

  return (
    <div className="relative">
      <Input
        className="bg-transparent border-none text-lg placeholder-muted-foreground mb-4"
        placeholder="Iphone 16 pro max"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      {showSuggestions && suggestions.length > 0 && (
        <ul
          ref={suggestionsRef}
          className="absolute w-full bg-background border border-input rounded-md mt-1 max-h-60 overflow-y-auto"
        >
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              className={`px-4 py-2 cursor-pointer ${
                index === focusedIndex
                  ? "bg-accent text-accent-foreground"
                  : "hover:bg-accent hover:text-accent-foreground"
              }`}
              onClick={() => handleSuggestionClick(suggestion)}
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
