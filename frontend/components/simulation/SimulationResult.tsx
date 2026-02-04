'use client';

import { SimulationResult as SimResultType } from '@/lib/queries';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SimulationResultProps {
    result: SimResultType | null;
}

export function SimulationResult({ result }: SimulationResultProps) {
    if (!result) return null;

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'Safe': return 'bg-green-500 hover:bg-green-600';
            case 'Caution': return 'bg-yellow-500 hover:bg-yellow-600';
            case 'Avoid': return 'bg-red-500 hover:bg-red-600';
            default: return 'bg-gray-500';
        }
    };

    const getIcon = (status: string) => {
        switch (status) {
            case 'Safe': return <CheckCircle className="h-6 w-6 text-green-600" />;
            case 'Caution': return <AlertTriangle className="h-6 w-6 text-yellow-600" />;
            case 'Avoid': return <AlertCircle className="h-6 w-6 text-red-600" />;
            default: return null;
        }
    };

    return (
        <Card className="w-full border-t-4 border-t-primary animate-in fade-in slide-in-from-bottom-5">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle>Analysis Result</CardTitle>
                    <Badge className={cn("text-lg px-4 py-1", getStatusColor(result.recommendation))}>
                        {result.recommendation}
                    </Badge>
                </div>
                {/* Confidence Bar moved up */}
                <div className="pt-4 space-y-1">
                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Confidence (based on available data)</span>
                        <span>{result.confidence}%</span>
                    </div>
                    <Progress value={result.confidence} className="h-1.5" />
                </div>
            </CardHeader>
            <CardContent className="space-y-6 pt-2">

                {/* Explanation */}
                <div className="bg-muted/30 p-4 rounded-lg border flex gap-4">
                    <div className="shrink-0 mt-0.5">
                        {getIcon(result.recommendation)}
                    </div>
                    <div>
                        <h4 className="font-semibold text-foreground text-sm">Assessment</h4>
                        <p className="text-sm text-muted-foreground leading-relaxed mt-1">
                            {result.explanation}
                        </p>
                    </div>
                </div>

                {/* Metrics Grid */}
                <div>
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Projected Impact</h4>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 border rounded-lg bg-card shadow-sm">
                            <div className="text-xs text-muted-foreground">Lowest Projected Balance</div>
                            <div className="text-xl font-bold mt-1 text-foreground">
                                ${result.projected_impact.lowest_balance.toLocaleString()}
                            </div>
                        </div>
                        <div className="p-4 border rounded-lg bg-card shadow-sm">
                            <div className="text-xs text-muted-foreground">Total Estimated Cost</div>
                            <div className="text-xl font-bold mt-1 text-foreground">
                                ${result.projected_impact.total_cost.toLocaleString()}
                            </div>
                        </div>
                    </div>
                </div>

            </CardContent>
        </Card>
    );
}
