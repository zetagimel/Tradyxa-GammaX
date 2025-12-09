import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Rocket, ExternalLink } from "lucide-react";

interface Product {
    name: string;
    description: string;
    url: string;
}

const PRODUCTS: Product[] = [
    {
        name: "Tradyxa Quant Dashboard",
        description: "AI-Driven NIFTY Options Prediction Lab",
        url: "https://tradyxa-alephx.pages.dev/",
    },
    {
        name: "Tradyxa Aegis Matrix",
        description: "NIFTY Options Intelligence System Using Trained ML Models",
        url: "https://tradyxa-betax.pages.dev/",
    },
];

export function OtherProductsTile() {
    return (
        <Card className="border-dashed">
            <CardHeader className="py-2 sm:py-3 px-3 sm:px-4">
                <CardTitle className="flex items-center gap-2 text-xs sm:text-sm">
                    <Rocket className="h-4 w-4 text-primary shrink-0" />
                    <span>Checkout our Other Products</span>
                </CardTitle>
            </CardHeader>

            <CardContent className="pt-0 pb-3 sm:pb-4 px-3 sm:px-4">
                <ul className="space-y-2 sm:space-y-3">
                    {PRODUCTS.map((product, idx) => (
                        <li
                            key={idx}
                            className="group p-2 sm:p-3 rounded-lg bg-gradient-to-r from-primary/5 to-primary/10 border border-primary/20 hover:border-primary/40 transition-all hover-elevate"
                        >
                            <a
                                href={product.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block"
                            >
                                <div className="flex items-start justify-between gap-2">
                                    <div className="flex-1 min-w-0">
                                        <h4 className="font-semibold text-xs sm:text-sm mb-0.5 text-primary flex items-center gap-1">
                                            {product.name}
                                            <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                                        </h4>
                                        <p className="text-xs text-muted-foreground leading-relaxed">
                                            {product.description}
                                        </p>
                                    </div>
                                </div>
                            </a>
                        </li>
                    ))}
                </ul>
            </CardContent>
        </Card>
    );
}
