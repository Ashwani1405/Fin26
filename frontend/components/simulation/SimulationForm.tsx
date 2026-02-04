'use client';

import { useState } from 'react';
import { useRunSimulation, SimulationRequest } from '@/lib/queries';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
// Removed invalid Select import
// I missed `select`. I will use standard HTML select or simpler buttons for decision type to avoid installing more deps if I can, OR just assume I should have added it.
// To be safe and fast, I will validly use a simple toggle or radio group using standard elements or basic buttons.
// Actually, `RadioGroup` is clean. But I didn't install that either.
// I'll use two buttons or a native select. Native select is fine for MVP.
import { Loader2, PlayCircle } from 'lucide-react';
import { toast } from 'sonner';

interface SimulationFormProps {
    onSimulationComplete: (result: any) => void;
}

export function SimulationForm({ onSimulationComplete }: SimulationFormProps) {
    const [amount, setAmount] = useState('');
    const [description, setDescription] = useState('');
    const [type, setType] = useState<'one_time' | 'recurring'>('one_time');

    const { mutate: runSimulation, isPending } = useRunSimulation();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!amount || !description) {
            toast.error("Please fill in all fields");
            return;
        }

        const payload = {
            amount: parseFloat(amount),
            description,
            decision_type: type
        };

        runSimulation(payload, {
            onSuccess: (data) => {
                onSimulationComplete(data);
                toast.success("Simulation complete");
            },
            onError: (err: any) => {
                toast.error(err.response?.data?.detail || "Simulation failed");
            }
        });
    };

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Scenario Analysis</CardTitle>
                <CardDescription>Analyze how a purchase impacts your long-term financial health.</CardDescription>
            </CardHeader>
            <form onSubmit={handleSubmit}>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="type">Expense Type</Label>
                        <div className="flex gap-2">
                            <Button
                                type="button"
                                variant={type === 'one_time' ? 'default' : 'outline'}
                                className="flex-1"
                                onClick={() => setType('one_time')}
                            >
                                One-Time
                            </Button>
                            <Button
                                type="button"
                                variant={type === 'recurring' ? 'default' : 'outline'}
                                className="flex-1"
                                onClick={() => setType('recurring')}
                            >
                                Recurring
                            </Button>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="amount">Amount ($)</Label>
                        <Input
                            id="amount"
                            type="number"
                            placeholder="5000"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            min="0"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Input
                            id="description"
                            type="text"
                            placeholder="e.g., Annual Vacation, Gym Membership"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                        />
                    </div>
                </CardContent>
                <CardFooter>
                    <Button disabled={isPending} className="w-full bg-blue-600 hover:bg-blue-700">
                        {isPending ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <PlayCircle className="mr-2 h-4 w-4" />
                                Analyze Impact
                            </>
                        )}
                    </Button>
                </CardFooter>
            </form>
        </Card>
    );
}
