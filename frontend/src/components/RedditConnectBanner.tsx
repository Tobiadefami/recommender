import React from "react";
import { Info, X } from "lucide-react";
import { Button } from "./ui/button";

interface RedditConnectBannerProps {
  onDismiss: () => void;
  onConnect: () => void;
}

export default function RedditConnectBanner({
  onDismiss,
  onConnect,
}: RedditConnectBannerProps) {
  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-lg p-4 mb-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Info className="w-5 h-5 text-primary" />
          <div>
            <p className="text-sm">
              Connect your Reddit account to enhance your search results.
              <span className="text-muted-foreground">
                {" "}
                You can manage this connection in your profile settings.
              </span>
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onConnect}
            className="text-sm"
          >
            Connect
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onDismiss}
            className="h-8 w-8"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
