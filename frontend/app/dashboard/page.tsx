'use client';

import { useFinanceStore } from '@/components/providers/StoreProvider';
import { Navbar } from '@/components/layout/Navbar';
import { CashflowBarChart } from '@/components/charts/CashflowBarChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowDown, ArrowUp, DollarSign, Wallet } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { useMemo, useEffect } from 'react';

// Simple Skeleton implementation since I didn't verify if shadcn skeleton was installed
function SimpleSkeleton({ className }: { className?: string }) {
    return <div className={`animate-pulse rounded-md bg-muted ${className}`} />;
}

import { DateRangeSelector } from '@/components/ui/date-range-selector';
import { isWithinInterval } from 'date-fns';

export default function DashboardPage() {
    // Read from global store
    const cashflowData = useFinanceStore((state) => state.monthlyCashflowData); // Updated property name
    const dateRange = useFinanceStore((state) => state.dateRange);
    const hasUploadedData = useFinanceStore((state) => state.hasUploadedData); // Explicit state check
    const appState = useFinanceStore((state) => state.appState);
    const fetchMonthlyCashflow = useFinanceStore((state) => state.fetchMonthlyCashflow);
    const isLoading = useFinanceStore((state) => state.isLoading);

    useEffect(() => {
        // Hydrate if missing
        if (!cashflowData || cashflowData.length === 0) {
            fetchMonthlyCashflow();
        }
    }, [cashflowData, fetchMonthlyCashflow]);

    // Filter data based on dateRange
    const filteredData = useMemo(() => {
        if (!cashflowData) return [];
        if (!dateRange.start || !dateRange.end) return cashflowData;

        return cashflowData.filter(item => {
            // Assuming item.month is "YYYY-MM"
            const date = new Date(item.month + '-01'); // Force 1st of month
            return isWithinInterval(date, {
                start: dateRange.start!,
                end: dateRange.end!
            });
        });
    }, [cashflowData, dateRange]);

    const summary = useMemo(() => {
        if (!filteredData || filteredData.length === 0) return null;

        // Calculate averages and totals based on the filtered data
        const totalIncome = filteredData.reduce((acc, curr) => acc + curr.income, 0);
        const totalExpense = filteredData.reduce((acc, curr) => acc + curr.expense, 0);
        const avgIncome = totalIncome / filteredData.length;
        const avgExpense = totalExpense / filteredData.length;
        const netBuffer = avgIncome - avgExpense;
        const savingsRate = avgIncome > 0 ? (netBuffer / avgIncome) * 100 : 0; // Prevent NaN

        return {
            avgIncome,
            avgExpense,
            netBuffer,
            savingsRate
        };
    }, [filteredData]);

    return (
        <div className="min-h-screen bg-muted/10">
            <Navbar />
            <div className="container py-10 space-y-8">
                <div className="flex items-center justify-between space-y-2">
                    <h2 className="text-3xl font-bold tracking-tight text-foreground/90">Dashboard</h2>
                    <DateRangeSelector />
                </div>

                {/* Summary Cards */}
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                    {!hasUploadedData ? ( // Strict check
                        <Card className="col-span-full border-dashed py-12">
                            <CardContent className="flex flex-col items-center justify-center space-y-4">
                                <div className="p-4 bg-muted rounded-full">
                                    <Wallet className="h-8 w-8 text-muted-foreground" />
                                </div>
                                <div className="text-center space-y-2">
                                    <h3 className="font-semibold text-lg text-foreground">Financial Overview Missing</h3>
                                    <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                                        We need your transaction history to analyze your income, expenses, and savings rate.
                                    </p>
                                </div>
                                <Button variant="outline" asChild className="mt-4">
                                    <Link href="/">Upload Transactions</Link>
                                </Button>
                            </CardContent>
                        </Card>
                    ) : summary ? (
                        <>
                            <Card className="hover:shadow-md transition-shadow">
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium text-muted-foreground">Avg Monthly Income</CardTitle>
                                    <ArrowUp className="h-4 w-4 text-emerald-500" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-foreground">${summary.avgIncome.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                                </CardContent>
                            </Card>
                            <Card className="hover:shadow-md transition-shadow">
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium text-muted-foreground">Avg Monthly Expense</CardTitle>
                                    <ArrowDown className="h-4 w-4 text-rose-500" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-foreground">${summary.avgExpense.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                                </CardContent>
                            </Card>
                            <Card className="hover:shadow-md transition-shadow">
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium text-muted-foreground">Net Monthly Buffer</CardTitle>
                                    <Wallet className="h-4 w-4 text-blue-500" />
                                </CardHeader>
                                <CardContent>
                                    <div className={`text-2xl font-bold ${summary.netBuffer >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                                        {summary.netBuffer >= 0 ? '+' : ''}${summary.netBuffer.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                                    </div>
                                </CardContent>
                            </Card>
                            <Card className="hover:shadow-md transition-shadow">
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium text-muted-foreground">Savings Rate</CardTitle>
                                    <DollarSign className="h-4 w-4 text-orange-500" />
                                </CardHeader>
                                <CardContent>
                                    <div className={`text-2xl font-bold ${summary.savingsRate >= 20 ? 'text-emerald-600' : summary.savingsRate > 0 ? 'text-yellow-600' : 'text-rose-600'}`}>
                                        {summary.savingsRate.toFixed(1)}%
                                    </div>
                                </CardContent>
                            </Card>
                        </>
                    ) : null}
                </div>

                {/* Charts Section */}
                {/* Using a grid with a sidebar potential or just full width focused view */}
                <div className="grid gap-6 md:grid-cols-12">
                    <div className="md:col-span-12">
                        {/* Wrapper for chart to ensure it feels like a dashboard widget */}
                        <div className="rounded-xl border bg-card text-card-foreground shadow-sm">
                            <div className="p-6">
                                <div className="mb-4">
                                    <h3 className="text-lg font-semibold">Cashflow History</h3>
                                    <p className="text-sm text-muted-foreground"> Income vs Expenses over time</p>
                                </div>
                                {isLoading ? (
                                    <div className="h-[350px] flex items-center justify-center">
                                        <SimpleSkeleton className="h-[300px] w-[90%]" />
                                    </div>
                                ) : filteredData && filteredData.length > 0 ? (
                                    <CashflowBarChart data={filteredData} />
                                ) : null}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
