import { FaEnvelope, FaLock, FaUser } from "react-icons/fa";
import React, { useEffect, useState } from "react";

import { AxiosError } from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/app/api";

interface LoginProps {
  onAuthSuccess: () => void;
}

const descriptions = [
  "Discover personalized product recommendations tailored to your interests and past searches.",
  "Stay ahead of the curve with our curated selection of trending products across various categories.",
  "Gain valuable insights into your shopping behavior with detailed search analytics.",
  "Seamlessly integrate your Reddit account to receive recommendations based on community discussions and trending topics.",
  "Watch informative YouTube reviews and unboxings to make informed purchasing decisions.",
  "Enjoy a fast and intuitive search experience with our intelligent autocomplete suggestions.",
];

export default function Login({ onAuthSuccess }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [currentDescription, setCurrentDescription] = useState("");
  const [fade, setFade] = useState(true);

  useEffect(() => {
    let currentDescriptionIndex = 0;
    const displayDescription = () => {
      const currentText = descriptions[currentDescriptionIndex];
      let charIndex = 0;

      const type = () => {
        if (charIndex < currentText.length) {
          setCurrentDescription(currentText.slice(0, ++charIndex));
          setTimeout(type, 100); // Typewriter effect
        } else {
          setFade(false);
          setTimeout(() => {
            setFade(true);
            currentDescriptionIndex =
              (currentDescriptionIndex + 1) % descriptions.length;
            setCurrentDescription("");
            displayDescription(); // Recursively display next description
          }, 1000); // Wait before showing the next one
        }
      };
      type();
    };

    displayDescription(); // Start the process
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      if (isLogin) {
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
        await api.post("/register", {
          username,
          email,
          password,
        });

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
    <div className="min-h-screen flex flex-col md:flex-row font-roboto">
      <div className="w-full md:w-1/2 flex items-center justify-center bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 text-white p-8">
        <div
          className={`text-2xl md:text-3xl lg:text-4xl font-light text-shadow-lg transition-opacity duration-500 ${
            fade ? "opacity-100" : "opacity-0"
          }`}
        >
          <p className="whitespace-pre-line leading-relaxed">
            {currentDescription}
          </p>
        </div>
      </div>
      <div className="w-full md:w-1/2 flex items-center justify-center bg-gray-50 p-4 md:p-8">
        <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg border border-gray-200">
          <h2 className="text-2xl font-semibold mb-6 text-center">
            {isLogin ? "Login" : "Sign Up"}
          </h2>

          {error && (
            <div className="bg-red-100 text-red-700 p-3 rounded-md mb-4">
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
                <FaUser className="absolute left-3 top-3 text-gray-400" />
              </div>
            </div>

            {!isLogin && (
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium mb-1"
                >
                  Email
                </label>
                <div className="relative">
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required={!isLogin}
                    className="pl-10"
                  />
                  <FaEnvelope className="absolute left-3 top-3 text-gray-400" />
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
                <FaLock className="absolute left-3 top-3 text-gray-400" />
              </div>
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
    </div>
  );
}
