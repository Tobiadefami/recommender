import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/app/api";
import { AxiosError } from "axios";

interface LoginProps {
  onAuthSuccess: () => void;
}

export default function Login({ onAuthSuccess }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      if (isLogin) {
        // Login
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const response = await api.post("/token", formData, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        localStorage.setItem("token", response.data.access_token);
        onAuthSuccess(); // Call the callback instead of using router
      } else {
        // Register
        await api.post("/register", {
          username,
          email,
          password,
        });

        // After successful registration, automatically log in
        const loginFormData = new URLSearchParams();
        loginFormData.append("username", username);
        loginFormData.append("password", password);

        const loginResponse = await api.post("/token", loginFormData, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        localStorage.setItem("token", loginResponse.data.access_token);
        onAuthSuccess(); // Call the callback instead of using router
      }
    } catch (error) {
      if (error instanceof AxiosError) {
        setError(error.response?.data?.detail || "An error occurred");
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md p-8 bg-card rounded-lg shadow-lg border border-border">
        <h2 className="text-2xl font-semibold mb-6">
          {isLogin ? "Login" : "Sign Up"}
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
            <Input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          {!isLogin && (
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required={!isLogin}
              />
            </div>
          )}

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium mb-1"
            >
              Password
            </label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Please wait..." : isLogin ? "Login" : "Sign Up"}
          </Button>
        </form>

        <div className="mt-4 text-center">
          <Button
            variant="link"
            onClick={() => {
              setIsLogin(!isLogin);
              setError("");
            }}
          >
            {isLogin
              ? "Don't have an account? Sign up"
              : "Already have an account? Login"}
          </Button>
        </div>
      </div>
    </div>
  );
}
