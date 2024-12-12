import { FaUser, FaLock, FaEnvelope } from "react-icons/fa";
import React, { useState } from "react";
import { AxiosError } from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/app/api";

interface LoginProps {
  onAuthSuccess: () => void;
}

export default function Login({ onAuthSuccess }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLogin, setIsLogin] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      if (isLogin) {
        // Login logic
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const response = await api.post("/token", formData, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        localStorage.setItem("token", response.data.access_token);
        onAuthSuccess();
      } else {
        // Registration logic
        await api.post("/register", {
          username,
          email,
          password,
        });

        // Automatically log in after successful registration
        const loginFormData = new URLSearchParams();
        loginFormData.append("username", username);
        loginFormData.append("password", password);

        const loginResponse = await api.post("/token", loginFormData, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        localStorage.setItem("token", loginResponse.data.access_token);
        onAuthSuccess();
      }
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(err.response?.data?.detail || "An error occurred");
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md p-8 bg-card rounded-lg shadow-lg border">
        <h2 className="text-2xl font-semibold mb-6 text-center">
          {isLogin ? "Sign In" : "Sign Up"}
        </h2>

        {error && (
          <div className="bg-destructive/10 text-destructive p-3 rounded-md mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium mb-1"
            >
              Username
            </label>
            <div className="relative">
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="pl-10"
              />
              <FaUser className="absolute left-3 top-3 text-muted-foreground" />
            </div>
          </div>

          {!isLogin && (
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">
                Email
              </label>
              <div className="relative">
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="pl-10"
                />
                <FaEnvelope className="absolute left-3 top-3 text-muted-foreground" />
              </div>
            </div>
          )}

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium mb-1"
            >
              Password
            </label>
            <div className="relative">
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="pl-10"
              />
              <FaLock className="absolute left-3 top-3 text-muted-foreground" />
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Please wait..." : isLogin ? "Sign In" : "Sign Up"}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-muted-foreground">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError("");
              setUsername("");
              setPassword("");
              setEmail("");
            }}
            className="text-primary hover:underline"
          >
            {isLogin ? "Sign up" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}
