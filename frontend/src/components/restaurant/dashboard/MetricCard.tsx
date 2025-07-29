import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  DollarSign,
  TrendingUp,
  BarChart,
  LucideIcon,
} from "lucide-react";
import axios from "axios";

import Card from "@/components/ui/Card";
import GlowingText from "@/components/ui/GlowingText";

// This shape matches what the backend writes to predicted.json
interface PredictedSummary {
  trainedAt: string;
  modelType: string;
  dishes: string[];
  predictedEarning: number[];
  bestAction: {
    dish: string;
    value: number;
  };
}

// Defines how each metric card will look
interface Metric {
  id: string;
  name: string;
  Icon: LucideIcon;
  value: number;
  unit: string;
}

const createMetrics = (summary: PredictedSummary): Metric[] => {
  const { dishes, predictedEarning, bestAction } = summary;

  const totalDishes = dishes.length;
  const earningsArray = predictedEarning;

  // Compute average predicted earning
  const avgEarning =
    earningsArray.reduce((sum, v) => sum + v, 0) / (earningsArray.length || 1);

  return [
    {
      id: "totalDishes",
      name: "Total Dishes",
      Icon: DollarSign,
      value: totalDishes,
      unit: "",
    },
    {
      id: "bestDish",
      name: `Best Dish: ${bestAction.dish}`,
      Icon: TrendingUp,
      value: parseFloat(bestAction.value.toFixed(2)),
      unit: "",
    },
    {
      id: "avgEarning",
      name: "Avg Predicted Earning",
      Icon: BarChart,
      value: parseFloat(avgEarning.toFixed(2)),
      unit: "",
    },
  ];
};

const MetricCard: React.FC = () => {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const authHeader = () => ({
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
    },
  });

  useEffect(() => {
    setLoading(true);
    axios
      .get<PredictedSummary>("/api/model/summary", authHeader())
      .then((res) => {
        setMetrics(createMetrics(res.data));
      })
      .catch((err) => {
        console.error("Failed to load model summary:", err);
        setError("Could not load metrics. Please try again.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="py-8 text-center text-gray-500">
        Loading metrics...
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-8 text-center text-red-500">
        {error}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {metrics.map((metric, idx) => {
        const bgShade = idx % 2 === 0 ? "bg-gray-100" : "bg-gray-200";
        const Icon = metric.Icon;

        return (
          <motion.div
            key={metric.id}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: idx * 0.1, duration: 0.5, ease: "easeOut" }}
          >
            <Card className={`${bgShade} flex flex-col justify-between p-5`} glow={false}>
              {/* Icon + Name */}
              <div className="flex justify-between items-start">
                <div className="flex items-center space-x-3">
                  <motion.div
                    whileHover={{ rotate: 360, transition: { duration: 1 } }}
                    className="rounded-lg bg-green-100 p-2 text-green-600"
                  >
                    <Icon size={18} />
                  </motion.div>
                  <h3 className="text-gray-800 font-medium">{metric.name}</h3>
                </div>
              </div>

              {/* Value */}
              <div className="mt-2 flex items-baseline">
                <GlowingText
                  text={metric.value}
                  variant="green"
                  hasCountUp
                  decimals={2}
                  className="text-2xl font-bold text-gray-900"
                />
                {metric.unit && <span className="ml-1 text-gray-700">{metric.unit}</span>}
              </div>
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
};

export default MetricCard;