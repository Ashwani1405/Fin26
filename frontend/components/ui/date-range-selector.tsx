'use client';

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from "@/components/ui/select";
import { useFinanceStore } from "@/components/providers/StoreProvider";
import { subMonths, startOfYear, subYears } from "date-fns";

export function DateRangeSelector() {
    const setDateRange = useFinanceStore((state) => state.setDateRange);

    const handleRangeChange = (value: string) => {
        const now = new Date();
        switch (value) {
            case '12_months':
                setDateRange({ start: subMonths(now, 12), end: now });
                break;
            case 'ytd':
                setDateRange({ start: startOfYear(now), end: now });
                break;
            case 'all_time':
            default:
                setDateRange({ start: null, end: null });
                break;
        }
    };

    return (
        <Select onValueChange={handleRangeChange} defaultValue="all_time">
            <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select Range" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value="all_time">All Time</SelectItem>
                <SelectItem value="12_months">Last 12 Months</SelectItem>
                <SelectItem value="ytd">Year to Date</SelectItem>
            </SelectContent>
        </Select>
    );
}
