// recommender/frontend/src/components/Autocomplete.tsx
import React, { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import api from "@/app/api";
import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDebouncedCallback } from "use-debounce";

interface AutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSuggestionSelect: (suggestion: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  showSuggestions: boolean;
  autoFocus?: boolean;
}

export default function Autocomplete({
  value,
  onChange,
  onSuggestionSelect,
  onSubmit,
  showSuggestions: initialShowSuggestions,
  autoFocus,
}: AutocompleteProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const [internalShowSuggestions, setInternalShowSuggestions] = useState(
    initialShowSuggestions,
  );
  const suggestionsRef = useRef<HTMLUListElement>(null);

  const debouncedFetchSuggestions = useDebouncedCallback(
    async (query: string) => {
      if (query.length <= 1 || !internalShowSuggestions) return;
      try {
        const response = await api.get(
          `/autocomplete?query=${encodeURIComponent(query)}`,
        );
        setSuggestions(response.data);
      } catch (error) {
        console.error("Failed to fetch suggestions:", error);
      }
    },
    300, // 300ms delay
  );

  useEffect(() => {
    debouncedFetchSuggestions(value);
  }, [value, debouncedFetchSuggestions]);

  const handleSuggestionClick = (suggestion: string) => {
    onSuggestionSelect(suggestion);
    setSuggestions([]);
    setInternalShowSuggestions(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    switch (e.key) {
      case "Enter":
        e.preventDefault();
        if (focusedIndex >= 0 && focusedIndex < suggestions.length) {
          onSuggestionSelect(suggestions[focusedIndex]);
        } else {
          onSubmit(e);
        }
        setSuggestions([]);
        setFocusedIndex(-1);
        setInternalShowSuggestions(false);
        break;
      case "ArrowDown":
        e.preventDefault();
        setFocusedIndex((prevIndex) =>
          prevIndex === suggestions.length - 1 ? 0 : prevIndex + 1,
        );
        break;
      case "ArrowUp":
        e.preventDefault();
        setFocusedIndex((prevIndex) =>
          prevIndex <= 0 ? suggestions.length - 1 : prevIndex - 1,
        );
        break;
      case "Escape":
        e.preventDefault();
        setSuggestions([]);
        setFocusedIndex(-1);
        setInternalShowSuggestions(false);
        break;
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    if (newValue.length > 1) {
      setInternalShowSuggestions(true);
    } else {
      setSuggestions([]);
    }
  };

  useEffect(() => {
    if (suggestionsRef.current && focusedIndex >= 0) {
      const focusedElement = suggestionsRef.current.children[
        focusedIndex
      ] as HTMLElement;
      focusedElement?.scrollIntoView({ block: "nearest" });
    }
  }, [focusedIndex]);

  const handleClear = () => {
    onChange("");
    setSuggestions([]);
    setFocusedIndex(-1);
    setInternalShowSuggestions(false);
  };

  const handleSearchClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (value.trim()) {
      onSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <div className="relative">
      <div className="relative flex items-center">
        <Input
          type="text"
          value={value}
          onChange={handleInputChange}
          className="bg-card/50 backdrop-blur-sm h-14 px-6 text-lg rounded-2xl shadow-sm
                     border-2 border-muted hover:border-muted-foreground/25 transition-colors
                     focus-visible:ring-2 focus-visible:ring-accent
                     focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          placeholder="What product are you looking for?"
          onKeyDown={handleKeyDown}
          autoFocus={autoFocus}
        />
        <div className="absolute right-2 flex items-center gap-1">
          {value && (
            <Button
              variant="ghost"
              size="sm"
              className="h-9 w-9 p-0 hover:bg-accent/50 rounded-xl"
              onClick={handleClear}
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-9 w-9 p-0 hover:bg-accent/50 rounded-xl"
            onClick={handleSearchClick}
          >
            <Search className="h-4 w-4 text-muted-foreground" />
          </Button>
        </div>
      </div>
      {internalShowSuggestions && suggestions.length > 0 && (
        <ul
          ref={suggestionsRef}
          className="absolute w-full bg-card/95 backdrop-blur-sm border border-border
                    rounded-xl mt-2 max-h-60 overflow-y-auto z-50 shadow-lg"
        >
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              className={`px-4 py-3 cursor-pointer border-b last:border-0 border-border/50
                        ${
                          index === focusedIndex
                            ? "bg-accent/50 text-accent-foreground"
                            : "hover:bg-accent/25"
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
