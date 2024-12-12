import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

interface LandingPageProps {
  onGetStarted: () => void;
}

export function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="min-h-screen flex flex-col font-roboto bg-background">
      <header className="p-4 md:p-6">
        <div className="flex justify-between items-center max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold">Recommendr</h1>
          <Button variant="ghost" onClick={onGetStarted}>
            Sign In
          </Button>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-4 md:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Smart Product Recommendations
          </h2>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Discover personalized product recommendations tailored to your
            interests and preferences
          </p>
          <Button size="lg" onClick={onGetStarted} className="text-lg px-8">
            Get Started
          </Button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full"
        >
          {/* Feature cards */}
          <div className="p-6 rounded-lg bg-card border">
            <h3 className="font-semibold mb-2">Personalized Results</h3>
            <p className="text-muted-foreground">
              Get recommendations based on your interests and search history
            </p>
          </div>
          <div className="p-6 rounded-lg bg-card border">
            <h3 className="font-semibold mb-2">Reddit Integration</h3>
            <p className="text-muted-foreground">
              Connect with Reddit to enhance your recommendations
            </p>
          </div>
          <div className="p-6 rounded-lg bg-card border">
            <h3 className="font-semibold mb-2">Smart Analytics</h3>
            <p className="text-muted-foreground">
              Track your search history and discover trends
            </p>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
