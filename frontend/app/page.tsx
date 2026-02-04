import { Navbar } from "@/components/layout/Navbar";
import { CSVUpload } from "@/components/forms/CSVUpload";
import { Card, CardContent } from "@/components/ui/card";
import { Info } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-muted/10">
      <Navbar />

      <div className="container py-12 md:py-24">
        <div className="flex flex-col items-center gap-8">
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Import Your Financial Data
            </h1>
            <p className="text-muted-foreground max-w-[600px] mx-auto">
              Upload your transaction history to unlock financial insights, cashflow forecasting, and scenario analysis.
            </p>
          </div>

          <CSVUpload />

          <Card className="w-full max-w-xl bg-blue-50/50 dark:bg-blue-900/10 border-blue-100 dark:border-blue-900">
            <CardContent className="flex gap-4 p-6">
              <Info className="h-5 w-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h4 className="font-semibold text-sm text-blue-900 dark:text-blue-100">Privacy & Security</h4>
                <p className="text-sm text-blue-700 dark:text-blue-300 leading-relaxed">
                  Your data is processed locally and never shared with third parties.
                  We only use the Description, Date, and Amount fields to generate insights.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
