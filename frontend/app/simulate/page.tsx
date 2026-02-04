'use client';

import { useState, useMemo } from 'react';
import { BrainCircuit } from 'lucide-react';
import { Navbar } from '@/components/layout/Navbar';
import { SimulationForm } from '@/components/simulation/SimulationForm';
import { SimulationResult } from '@/components/simulation/SimulationResult';
import { SimulationResult as SimResultType } from '@/lib/queries';
import { useFinanceStore } from '@/components/providers/StoreProvider';
import { Card, CardContent } from '@/components/ui/card'; // Import Card components
import Link from 'next/link'; // Import Link
import { Button } from '@/components/ui/button'; // Import Button

export default function SimulatePage() {
    const [result, setResult] = useState<SimResultType | null>(null);
    const cashflowData = useFinanceStore((state) => state.monthlyCashflowData); // Use correct property
    const appState = useFinanceStore((state) => state.appState);
    const fetchMonthlyCashflow = useFinanceStore((state) => state.fetchMonthlyCashflow);

    useMemo(() => {
        // Hydrate if missing and logic suggests we should have it (not enforcing strict empty check as it might be fine to sim without data but better with it)
        if (!cashflowData || cashflowData.length === 0) {
            fetchMonthlyCashflow();
        }
    }, [cashflowData, fetchMonthlyCashflow]);

    // Calculate context based on global data
    const context = useMemo(() => {
        if (!cashflowData || cashflowData.length === 0) return null;
        const totalIncome = cashflowData.reduce((acc, curr) => acc + curr.income, 0);
        const avgIncome = totalIncome / cashflowData.length;
        const totalExpense = cashflowData.reduce((acc, curr) => acc + curr.expense, 0);
        const avgExpense = totalExpense / cashflowData.length;
        const buffer = avgIncome - avgExpense;
        return { avgIncome, buffer };
    }, [cashflowData]);

    const isDataMissing = appState === "EMPTY";

    return (
        <div className="min-h-screen bg-muted/10">
            <Navbar />
            <div className="container py-12 space-y-10">
                <div className="text-center space-y-4 max-w-2xl mx-auto">
                    <h1 className="text-4xl font-bold tracking-tight text-foreground">Decision Simulator</h1>
                    <p className="text-lg text-muted-foreground leading-relaxed">
                        Test financial decisions before you make them. See how big purchases affect your future runway and financial health.
                    </p>
                </div>

                <div className="grid gap-8 lg:grid-cols-12 items-start">
                    <div className="lg:col-span-4 lg:sticky lg:top-8 space-y-4">
                        {isDataMissing && (
                            <Card className="border-orange-200 bg-orange-50/50">
                                <CardContent className="p-4 flex flex-col space-y-3">
                                    <div className="flex items-center space-x-2 text-orange-700">
                                        <BrainCircuit className="h-5 w-5" />
                                        <span className="font-semibold text-sm">Data Recommended</span>
                                    </div>
                                    <p className="text-xs text-orange-800/80">
                                        Simulations are more accurate with your transaction history.
                                    </p>
                                    <Button variant="outline" size="sm" className="w-full bg-white/50 border-orange-200 text-orange-800 hover:bg-white" asChild>
                                        <Link href="/">Upload Data</Link>
                                    </Button>
                                </CardContent>
                            </Card>
                        )}
                        <SimulationForm onSimulationComplete={setResult} />
                    </div>
                    <div className="lg:col-span-8">
                        {result ? (
                            <SimulationResult result={result} />
                        ) : (
                            <div className="h-full min-h-[400px] flex flex-col items-center justify-center border-2 border-dashed rounded-xl bg-muted/5 text-muted-foreground p-8 text-center space-y-4">
                                <div className="p-4 bg-muted rounded-full opacity-50">
                                    <BrainCircuit className="h-10 w-10" />
                                </div>
                                <div className="max-w-xs">
                                    <h3 className="font-semibold text-foreground">Ready to Analyze</h3>
                                    {context ? (
                                        <p className="text-sm mt-1">
                                            Based on your average monthly buffer of <span className="font-semibold text-emerald-600">${context.buffer.toFixed(0)}</span>,
                                            see how a new expense fits in.
                                        </p>
                                    ) : (
                                        <p className="text-sm mt-1">
                                            Enter decision details on the left to generate a projection.
                                        </p>
                                    )}
                                </div>
                                {/* No redundant CTA here if we have key CTA in the sidebar warning */}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
