// recommender/frontend/src/components/Autocomplete.tsx
import React, { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import api from "@/app/api";
import { useCallback } from "react";
import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
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
  showSuggestions: initialShowSuggestions,
}: AutocompleteProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const [internalShowSuggestions, setInternalShowSuggestions] = useState(
    initialShowSuggestions,
  );
  const suggestionsRef = useRef<HTMLUListElement>(null);

  const fetchSuggestions = useCallback(async () => {
    try {
      const response = await api.get(
        `/autocomplete?query=${encodeURIComponent(value)}`,
      );
      setSuggestions(response.data);
    } catch (error) {
      console.error("Failed to fetch suggestions:", error);
    }
  }, [value]);

  useEffect(() => {
    if (value.length > 1 && internalShowSuggestions) {
      fetchSuggestions();
    } else {
      setSuggestions([]);
    }
  }, [value, fetchSuggestions, internalShowSuggestions]);

  useEffect(() => {
    setInternalShowSuggestions(initialShowSuggestions);
  }, [initialShowSuggestions]);

  const handleSuggestionClick = (suggestion: string) => {
    onSuggestionSelect(suggestion);
    setSuggestions([]);
    setInternalShowSuggestions(false);
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
      setInternalShowSuggestions(false);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setFocusedIndex((prevIndex) =>
        prevIndex === suggestions.length - 1 ? 0 : prevIndex + 1,
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setFocusedIndex((prevIndex) =>
        prevIndex <= 0 ? suggestions.length - 1 : prevIndex - 1,
      );
    } else if (e.key === "Escape") {
      e.preventDefault();
      setSuggestions([]);
      setFocusedIndex(-1);
      setInternalShowSuggestions(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    if (newValue.length > 1) {
      setInternalShowSuggestions(true);
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

  const handleClear = () => {
    onChange("");
    setSuggestions([]);
    setFocusedIndex(-1);
    setInternalShowSuggestions(false);
  };
  const handleSearchClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (value.trim()) {
      onSubmit(e as any);
    }
  };

  return (
    <div className="relative">
      <div className="relative flex items-center">
        <Input
          className="bg-transparent pr-20 text-lg placeholder-muted-foreground"
          placeholder="Iphone 16 pro max"
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
        />
        <div className="absolute right-2 flex items-center gap-1">
          {value && (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 hover:bg-transparent"
              onClick={handleClear}
            >
              <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 hover:bg-transparent"
            onClick={handleSearchClick}
          >
            <Search className="h-4 w-4 text-muted-foreground hover:text-foreground" />
          </Button>
        </div>
      </div>
      {internalShowSuggestions && suggestions.length > 0 && (
        <ul
          ref={suggestionsRef}
          className="absolute w-full bg-background border border-input rounded-md mt-1 max-h-60 overflow-y-auto z-50"
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
