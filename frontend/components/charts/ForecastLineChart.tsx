'use client';

import { Area, ComposedChart, CartesianGrid, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ForecastData } from '@/lib/queries';

interface ForecastLineChartProps {
    data: ForecastData[];
}

export function ForecastLineChart({ data }: ForecastLineChartProps) {
    if (!data || !Array.isArray(data) || data.length === 0) {
        console.warn("ForecastLineChart received invalid data:", data);
        return (
            <div className="h-[350px] flex items-center justify-center text-muted-foreground">
                No forecast data available
            </div>
        );
    }

    // Transform data: Calculate `band_height` for area stacking and format dates
    const chartData = data.map(d => {
        const date = new Date(d.date + '-01'); // Append day to parse YYYY-MM
        return {
            date: d.date,
            displayDate: date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
            predicted_balance: d.predicted_balance,
            lower_bound: d.lower_bound,
            // Band height: The area between lower and upper. For Recharts stacking.
            band_height: d.upper_bound - d.lower_bound,
            upper_bound: d.upper_bound,
        };
    });

    return (
        <Card className="w-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg">Cashflow Forecast</CardTitle>
                <CardDescription>
                    Projected balance for the next 6 months with uncertainty bounds.
                </CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
                <ResponsiveContainer width="100%" height={350}>
                    <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="gradientBand" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-muted/50" />
                        <XAxis
                            dataKey="displayDate"
                            stroke="hsl(var(--muted-foreground))"
                            fontSize={11}
                            tickLine={false}
                            axisLine={false}
                            tickMargin={8}
                        />
                        <YAxis
                            stroke="hsl(var(--muted-foreground))"
                            fontSize={11}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                            width={50}
                        />
                        <Tooltip
                            contentStyle={{
                                borderRadius: '8px',
                                border: '1px solid hsl(var(--border))',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                                backgroundColor: 'hsl(var(--background))'
                            }}
                            formatter={(value, name) => {
                                if (value === undefined) return ['', ''];
                                const labels: Record<string, string> = {
                                    'predicted_balance': 'Predicted',
                                    'lower_bound': 'Conservative',
                                    'upper_bound': 'Optimistic',
                                };
                                return [`$${Number(value).toLocaleString()}`, labels[String(name)] || String(name)];
                            }}
                            labelFormatter={(label) => `Month: ${label}`}
                        />

                        {/* Confidence Band: Lower bound as base, then the band_height stacked on top */}
                        {/* This creates a visual "band" between lower and upper */}
                        <Area
                            type="monotone"
                            dataKey="lower_bound"
                            stackId="band"
                            stroke="none"
                            fill="transparent"
                            legendType="none"
                        />
                        <Area
                            type="monotone"
                            dataKey="band_height"
                            stackId="band"
                            stroke="none"
                            fill="url(#gradientBand)"
                            legendType="none"
                            name="Confidence Range"
                        />

                        {/* Main Prediction Line - Prominent */}
                        <Line
                            type="monotone"
                            dataKey="predicted_balance"
                            stroke="#2563eb"
                            strokeWidth={3}
                            dot={{ r: 4, fill: '#2563eb', strokeWidth: 2, stroke: '#fff' }}
                            activeDot={{ r: 6, fill: '#2563eb', strokeWidth: 2, stroke: '#fff' }}
                            name="Predicted Balance"
                        />

                        {/* Bounds as subtle dashed lines */}
                        <Line
                            type="monotone"
                            dataKey="upper_bound"
                            stroke="#93c5fd"
                            strokeDasharray="4 4"
                            strokeWidth={1.5}
                            dot={false}
                            name="Optimistic"
                            legendType="none"
                        />
                        <Line
                            type="monotone"
                            dataKey="lower_bound"
                            stroke="#93c5fd"
                            strokeDasharray="4 4"
                            strokeWidth={1.5}
                            dot={false}
                            name="Conservative"
                            legendType="none"
                        />

                        {/* Custom Legend - Only show the main line */}
                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            formatter={(value) => {
                                if (value === 'Predicted Balance') return <span className="text-sm font-medium">Predicted Balance</span>;
                                return null;
                            }}
                        />
                    </ComposedChart>
                </ResponsiveContainer>
                <p className="text-xs text-muted-foreground text-center mt-2">
                    Shaded area represents the 95% confidence interval
                </p>
            </CardContent>
        </Card>
    );
}
