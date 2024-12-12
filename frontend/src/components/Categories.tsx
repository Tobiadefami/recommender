import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Laptop,
  Smartphone,
  Camera,
  Watch,
  Headphones,
  Gamepad,
  Car,
  Tv,
  ChevronDown,
} from "lucide-react";

const categories = [
  {
    name: "Smartphones",
    icon: Smartphone,
    products: [
      "iPhone 15 Pro",
      "Samsung Galaxy S24 Ultra",
      "Google Pixel 8 Pro",
      "OnePlus 12",
      "Xiaomi 14 Pro",
    ],
  },
  {
    name: "Computers",
    icon: Laptop,
    products: [
      "MacBook Pro M3",
      "Dell XPS 13",
      "Lenovo ThinkPad X1",
      "HP Spectre x360",
      "ASUS ROG Zephyrus",
    ],
  },
  {
    name: "Cameras",
    icon: Camera,
    products: [
      "Sony a7 IV",
      "Canon R6 Mark II",
      "Fujifilm X-T5",
      "Nikon Z6 II",
      "Panasonic GH6",
    ],
  },
  {
    name: "Wearables",
    icon: Watch,
    products: [
      "Apple Watch Series 9",
      "Samsung Galaxy Watch 6",
      "Garmin Fenix 7",
      "Fitbit Sense 2",
      "WHOOP 4.0",
    ],
  },
  {
    name: "Audio",
    icon: Headphones,
    products: [
      "AirPods Pro 2",
      "Sony WH-1000XM5",
      "Bose QC Ultra",
      "Sennheiser Momentum 4",
      "Samsung Galaxy Buds 2 Pro",
    ],
  },
  {
    name: "Gaming",
    icon: Gamepad,
    products: [
      "PS5",
      "Xbox Series X",
      "Nintendo Switch OLED",
      "Steam Deck",
      "ROG Ally",
    ],
  },
  {
    name: "TVs",
    icon: Tv,
    products: [
      "LG C3 OLED",
      "Samsung S95C",
      "Sony A95L",
      "TCL QM8",
      "Hisense U8K",
    ],
  },
  {
    name: "Vehicles",
    icon: Car,
    products: [
      "Tesla Model 3",
      "Ford Mustang Mach-E",
      "Porsche Taycan",
      "BMW i4",
      "Hyundai IONIQ 6",
    ],
  },
];

interface CategorySelectorProps {
  onCategorySelect: (product: string) => void;
}

const CategorySelector: React.FC<CategorySelectorProps> = ({
  onCategorySelect,
}) => {
  return (
    <Card className="bg-card/50 backdrop-blur-sm border border-border/50 hover:border-border transition-colors">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          Browse by category
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {categories.map((category) => {
            const Icon = category.icon;
            return (
              <DropdownMenu key={category.name}>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="flex flex-col items-center gap-2 h-auto py-4 w-full hover:bg-accent/50 transition-colors rounded-xl group"
                  >
                    <Icon className="w-6 h-6 text-muted-foreground" />
                    <span className="text-sm font-medium">{category.name}</span>
                    <ChevronDown className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="center" className="w-48">
                  {category.products.map((product) => (
                    <DropdownMenuItem
                      key={product}
                      onClick={() => onCategorySelect(product)}
                      className="cursor-pointer"
                    >
                      {product}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default CategorySelector;
