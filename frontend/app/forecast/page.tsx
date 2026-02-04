'use client';

import { useFinanceStore } from '@/components/providers/StoreProvider';
import { useState, useEffect } from 'react';
import { Navbar } from '@/components/layout/Navbar';
import { ForecastLineChart } from '@/components/charts/ForecastLineChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { AlertTriangle, TrendingUp } from 'lucide-react';

export default function ForecastPage() {
    // Read from global store
    const appState = useFinanceStore((state) => state.appState);
    const forecastData = useFinanceStore((state) => state.forecastData);
    const setForecastData = useFinanceStore((state) => state.setForecastData);
    const fetchForecastData = useFinanceStore((state) => state.fetchForecastData);
    const storeLoading = useFinanceStore((state) => state.isLoading);

    useEffect(() => {
        // Hydrate logic: Fetch if we have uploaded data (or if fetch ensures it) 
        // AND we don't have forecast data yet.
        // Actually, if appState is EMPTY, we probably can't fetch forecast successfully 
        // (unless backend persists uploads across sessions, which it does for MVP if DB is valid).

        // Optimistic fetch: Try fetching if we don't have data.
        if (!forecastData || forecastData.length === 0) {
            fetchForecastData();
        }
    }, [forecastData, fetchForecastData]);

    const showEmptyState = appState === "EMPTY" && (!forecastData || forecastData.length === 0);
    // If we are fetching, show loading. If we have data, show content.
    const showLoading = storeLoading;
    const showContent = forecastData && forecastData.length > 0;

    return (
        <div className="min-h-screen bg-muted/10">
            <Navbar />
            <div className="container py-10 space-y-8">
                <div className="flex items-center justify-between space-y-2">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">Cashflow Forecast</h2>
                        <p className="text-muted-foreground">
                            Probabilistic projection of your future finances.
                        </p>
                    </div>
                </div>

                <div className="grid gap-8 lg:grid-cols-12">
                    {/* Main Chart Area */}
                    <div className="lg:col-span-8 space-y-6">
                        {showLoading ? (
                            <Card className="h-[450px] flex flex-col items-center justify-center space-y-4">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                                <p className="text-muted-foreground">Generating forecast...</p>
                            </Card>
                        ) : showContent ? (
                            <ForecastLineChart data={forecastData} />
                        ) : (
                            // Empty State (appState === "EMPTY")
                            <Card className="h-[450px] flex flex-col items-center justify-center space-y-4 border-dashed">
                                <div className="p-4 bg-muted rounded-full">
                                    <TrendingUp className="h-8 w-8 text-muted-foreground" />
                                </div>
                                <div className="text-center space-y-1">
                                    <h3 className="font-semibold text-lg">No Forecast Data</h3>
                                    <p className="text-sm text-muted-foreground max-w-sm">
                                        Upload your transaction history to see a projection of your future finances.
                                    </p>
                                </div>
                                <Button variant="default" asChild>
                                    <Link href="/">Upload Transactions</Link>
                                </Button>
                            </Card>
                        )}
                    </div>

                    {/* Sidebar Context (Right) */}
                    <div className="lg:col-span-4 space-y-6">
                        {showContent && (
                            <>
                                {/* Confidence Card */}
                                <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/30 border-emerald-200 dark:border-emerald-800">
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium text-emerald-700 dark:text-emerald-300">Model Confidence</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-3xl font-bold tracking-tight text-emerald-800 dark:text-emerald-100">85%</span>
                                            <TrendingUp className="h-5 w-5 text-emerald-600" />
                                        </div>
                                        <Progress value={85} className="h-2 bg-emerald-100 dark:bg-emerald-900" />
                                        <p className="text-xs text-emerald-700/80 dark:text-emerald-300/80 mt-3 leading-relaxed">
                                            Based on {forecastData.length > 3 ? 'sufficient' : 'limited'} historical data. Confidence may decrease for months further out.
                                        </p>
                                    </CardContent>
                                </Card>

                                {/* Understanding Your Forecast */}
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                                            <AlertTriangle className="h-4 w-4 text-blue-600" />
                                            Understanding This Chart
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="text-sm text-muted-foreground space-y-3">
                                        <div className="flex items-start gap-3">
                                            <div className="w-4 h-1 mt-2 bg-blue-600 rounded-full shrink-0"></div>
                                            <div>
                                                <strong className="text-foreground">Blue Line</strong>
                                                <p>Your most likely future balance based on spending patterns.</p>
                                            </div>
                                        </div>
                                        <div className="flex items-start gap-3">
                                            <div className="w-4 h-4 mt-1 bg-blue-500/20 rounded shrink-0"></div>
                                            <div>
                                                <strong className="text-foreground">Shaded Area</strong>
                                                <p>Range of possible outcomes (think of it as "best case" to "worst case").</p>
                                            </div>
                                        </div>
                                        <p className="pt-2 border-t text-xs">
                                            💡 <span className="font-medium">Tip:</span> A wider band means more uncertainty. Keep tracking your expenses to improve accuracy!
                                        </p>
                                    </CardContent>
                                </Card>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
