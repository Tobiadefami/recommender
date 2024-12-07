import React, { useEffect, useState } from "react";

import { X } from "lucide-react"; // Only import what you use
import api from "@/app/api";

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
  const [isLoading, setIsLoading] = useState(false);
  const [redditStatus, setRedditStatus] = useState<RedditStatus>({
    connected: false,
  });
  const [activeTab, setActiveTab] = useState<string>("oauth");

  const fetchRedditStatus = async () => {
    try {
      const response = await api.get("/reddit/status");
      setRedditStatus(response.data);
    } catch (error) {
      console.error("Failed to fetch Reddit connection status:", error);
    }
  };

  useEffect(() => {
    if (isOpen) fetchRedditStatus();
  }, [isOpen]);

  const handleToggleReddit = async () => {
    setIsLoading(true);

    try {
      if (redditStatus.connected) {
        await api.post("/reddit/deactivate");
        setRedditStatus((prev) => ({ ...prev, connected: false }));
      } else {
        const response = await api.post("/reddit/activate");
        if (response.data.url) {
          window.location.href = response.data.url;
          return;
        }
        setRedditStatus((prev) => ({ ...prev, connected: true }));
      }
    } catch (error) {
      console.error("Failed to update Reddit connection:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderContent = () => {
    if (activeTab === "oauth") {
      return (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">OAuth Settings</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <div>
                <h4 className="text-sm font-medium">Reddit Connection</h4>
                <p className="text-sm text-muted-foreground">
                  {redditStatus.connected
                    ? `Connected as ${redditStatus.username}`
                    : "Connect your Reddit account for better recommendations."}
                </p>
              </div>
              <input
                type="checkbox"
                className="toggle-switch"
                checked={redditStatus.connected}
                onChange={handleToggleReddit}
                disabled={isLoading}
              />
            </div>
            {redditStatus.connected && redditStatus.lastSync && (
              <p className="text-xs text-muted-foreground">
                Last synced:{" "}
                {new Date(redditStatus.lastSync).toLocaleDateString()}
              </p>
            )}
          </div>
        </div>
      );
    }

    return <p>Select a setting from the left to view details.</p>;
  };

  return (
    <div
      className={`fixed inset-0 bg-gray-100 p-4 transition-transform ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Settings</h2>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-800">
          <X className="h-6 w-6" />
        </button>
      </div>

      <div className="flex space-x-4">
        {/* Sidebar */}
        <div className="w-1/4 bg-gray-200 p-4 rounded-lg">
          <ul className="space-y-2">
            <li>
              <button
                className={`w-full text-left ${activeTab === "oauth" ? "font-bold" : ""}`}
                onClick={() => setActiveTab("oauth")}
              >
                OAuth
              </button>
            </li>
          </ul>
        </div>

        {/* Content Area */}
        <div className="w-3/4 bg-white p-4 rounded-lg shadow">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}
