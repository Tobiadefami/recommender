"use client";

import { useCallback } from "react";
import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { X, Link2, User, Bell, Shield, Palette } from "lucide-react";
import { cn } from "@/lib/utils";
import api from "@/app/api";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
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

interface UserProfile {
  username: string;
  email: string;
  notifications: {
    email: boolean;
    recommendations: boolean;
  };
  theme: "light" | "dark" | "system";
  privacy: {
    showHistory: boolean;
    shareData: boolean;
  };
}

interface TabItem {
  id: string;
  label: string;
  icon: React.ReactNode;
}

const tabs: TabItem[] = [
  { id: "profile", label: "Profile", icon: <User className="w-4 h-4" /> },
  {
    id: "connections",
    label: "Connections",
    icon: <Link2 className="w-4 h-4" />,
  },
  {
    id: "notifications",
    label: "Notifications",
    icon: <Bell className="w-4 h-4" />,
  },
  {
    id: "appearance",
    label: "Appearance",
    icon: <Palette className="w-4 h-4" />,
  },
  { id: "privacy", label: "Privacy", icon: <Shield className="w-4 h-4" /> },
];

export default function ProfileSettings({
  isOpen,
  onClose,
}: ProfileSettingsProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [redditStatus, setRedditStatus] = useState<RedditStatus>({
    connected: false,
  });
  const [activeTab, setActiveTab] = useState<string>("profile");
  const [userProfile, setUserProfile] = useState<UserProfile>({
    username: "",
    email: "",
    notifications: {
      email: true,
      recommendations: true,
    },
    theme: "system",
    privacy: {
      showHistory: true,
      shareData: true,
    },
  });

  const fetchUserProfile = useCallback(async () => {
    try {
      const response = await api.get("/users/me");
      setUserProfile(response.data);
    } catch (error) {
      console.error("Failed to fetch user profile:", error);
      toast({
        title: "Error",
        description: "Failed to load user profile",
        variant: "destructive",
      });
    }
  }, [toast]);

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
      fetchUserProfile();
      fetchRedditStatus();
    }
  }, [isOpen, fetchUserProfile, fetchRedditStatus]);

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

  const updateProfile = async (updates: Partial<UserProfile>) => {
    try {
      await api.patch("/users/me", updates);
      setUserProfile((prev) => ({ ...prev, ...updates }));
      toast({
        title: "Success",
        description: "Profile updated successfully",
      });
    } catch (error) {
      console.error("Failed to update profile:", error);
      toast({
        title: "Error",
        description: "Failed to update profile",
        variant: "destructive",
      });
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case "profile":
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold">Profile Settings</h3>
              <p className="text-sm text-muted-foreground">
                Manage your personal information
              </p>
            </div>
            <div className="h-[1px] w-full bg-border" />
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  value={userProfile.username}
                  onChange={(e) =>
                    setUserProfile((prev) => ({
                      ...prev,
                      username: e.target.value,
                    }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={userProfile.email}
                  onChange={(e) =>
                    setUserProfile((prev) => ({
                      ...prev,
                      email: e.target.value,
                    }))
                  }
                />
              </div>
              <Button
                onClick={() =>
                  updateProfile({
                    username: userProfile.username,
                    email: userProfile.email,
                  })
                }
              >
                Save Changes
              </Button>
            </div>
          </div>
        );

      case "connections":
        return (
          <div className="space-y-6">
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
        );

      case "notifications":
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold">Notification Settings</h3>
              <p className="text-sm text-muted-foreground">
                Manage your notification preferences
              </p>
            </div>
            <div className="h-[1px] w-full bg-border" />
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive updates via email
                  </p>
                </div>
                <Switch
                  checked={userProfile.notifications.email}
                  onCheckedChange={(checked) =>
                    updateProfile({
                      notifications: {
                        ...userProfile.notifications,
                        email: checked,
                      },
                    })
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Recommendation Updates</Label>
                  <p className="text-sm text-muted-foreground">
                    Get notified about new recommendations
                  </p>
                </div>
                <Switch
                  checked={userProfile.notifications.recommendations}
                  onCheckedChange={(checked) =>
                    updateProfile({
                      notifications: {
                        ...userProfile.notifications,
                        recommendations: checked,
                      },
                    })
                  }
                />
              </div>
            </div>
          </div>
        );

      case "appearance":
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold">Appearance Settings</h3>
              <p className="text-sm text-muted-foreground">
                Customize your visual preferences
              </p>
            </div>
            <div className="h-[1px] w-full bg-border" />
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Theme Preference</Label>
                  <p className="text-sm text-muted-foreground">
                    Choose your preferred theme
                  </p>
                </div>
                <Select
                  value={userProfile.theme}
                  onValueChange={(value: "light" | "dark" | "system") =>
                    updateProfile({ theme: value })
                  }
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select theme" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        );

      case "privacy":
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold">Privacy Settings</h3>
              <p className="text-sm text-muted-foreground">
                Manage your privacy preferences
              </p>
            </div>
            <div className="h-[1px] w-full bg-border" />
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Search History</Label>
                  <p className="text-sm text-muted-foreground">
                    Show your search history
                  </p>
                </div>
                <Switch
                  checked={userProfile.privacy.showHistory}
                  onCheckedChange={(checked) =>
                    updateProfile({
                      privacy: {
                        ...userProfile.privacy,
                        showHistory: checked,
                      },
                    })
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Data Sharing</Label>
                  <p className="text-sm text-muted-foreground">
                    Share anonymous usage data
                  </p>
                </div>
                <Switch
                  checked={userProfile.privacy.shareData}
                  onCheckedChange={(checked) =>
                    updateProfile({
                      privacy: {
                        ...userProfile.privacy,
                        shareData: checked,
                      },
                    })
                  }
                />
              </div>
            </div>
          </div>
        );

      default:
        return null;
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
            <div className="flex flex-1 overflow-hidden">
              {/* Sidebar */}
              <div className="w-[30%] border-r">
                <nav className="p-2">
                  {tabs.map((tab) => (
                    <Button
                      key={tab.id}
                      variant={activeTab === tab.id ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start gap-2 px-2",
                        activeTab === tab.id && "bg-accent",
                      )}
                      onClick={() => setActiveTab(tab.id)}
                    >
                      {tab.icon}
                      {tab.label}
                    </Button>
                  ))}
                </nav>
              </div>

              {/* Main Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {renderContent()}
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
