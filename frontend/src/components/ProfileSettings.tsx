"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import api from "@/app/api";
import { useToast } from "@/hooks/use-toast";
import { Toaster } from "./ui/toaster";
import { createPortal } from "react-dom";

interface ProfileSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

interface RedditStatus {
  connected: boolean;
  username?: string;
  lastSync?: string;
}

export default function ProfileSettings({
  isOpen,
  onClose,
}: ProfileSettingsProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [redditStatus, setRedditStatus] = useState<RedditStatus>({
    connected: false,
  });

  const fetchRedditStatus = useCallback(async () => {
    try {
      const response = await api.get("/reddit/status");
      setRedditStatus(response.data);
    } catch (error) {
      console.error("Failed to fetch Reddit connection status:", error);
      toast({
        title: "Error",
        description: "Failed to load Reddit connection status",
        variant: "destructive",
      });
    }
  }, [toast]);

  useEffect(() => {
    if (isOpen) {
      fetchRedditStatus();
    }
  }, [isOpen, fetchRedditStatus]);

  const handleToggleReddit = async () => {
    setIsLoading(true);
    try {
      if (redditStatus.connected) {
        await api.post("/reddit/deactivate");
        setRedditStatus((prev) => ({ ...prev, connected: false }));
        toast({
          title: "Success",
          description: "Reddit connection removed",
        });
      } else {
        const response = await api.get("/reddit/auth");
        if (response.data.url) {
          window.location.href = response.data.url;
          return;
        }
      }
    } catch (error) {
      console.error("Failed to update Reddit connection:", error);
      toast({
        title: "Error",
        description: "Failed to update Reddit connection",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <>
      <div
        className={cn(
          "fixed inset-0 bg-background/80 backdrop-blur-sm z-50 transition-opacity duration-300",
          isOpen ? "opacity-100" : "opacity-0",
        )}
      >
        <div className="absolute right-0 top-0 h-full w-[400px] bg-background border-l shadow-lg">
          <div className="flex h-full flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h2 className="text-lg font-semibold">Settings</h2>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Content */}
            <div className="flex flex-1 overflow-hidden p-6">
              <div className="space-y-6 w-full">
                <div>
                  <h3 className="text-lg font-semibold">Connected Accounts</h3>
                  <p className="text-sm text-muted-foreground">
                    Manage your connected accounts and services
                  </p>
                </div>
                <div className="h-[1px] w-full bg-border" />
                <div className="space-y-8">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <h4 className="text-sm font-medium">Reddit Connection</h4>
                      <p className="text-sm text-muted-foreground">
                        {redditStatus.connected
                          ? `Connected as ${redditStatus.username}`
                          : "Connect your Reddit account for better recommendations"}
                      </p>
                      {redditStatus.connected && redditStatus.lastSync && (
                        <p className="text-xs text-muted-foreground">
                          Last synced:{" "}
                          {new Date(redditStatus.lastSync).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    <Switch
                      checked={redditStatus.connected}
                      onCheckedChange={handleToggleReddit}
                      disabled={isLoading}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Toaster Component for displaying toasts */}
      <Toaster />
    </>,
    document.body,
  );
}
