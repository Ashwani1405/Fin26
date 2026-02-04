import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from './api';

// Types
export interface Transaction {
    id?: string;
    date: string;
    amount: number;
    description: string;
    category?: string;
}

export interface CashflowData {
    month: string;
    income: number;
    expense: number;
    net: number;
}

export interface ForecastData {
    date: string;
    predicted_balance: number;
    lower_bound: number;
    upper_bound: number;
}

export interface SimulationRequest {
    user_id: string; // Added user_id
    decision_type: string; // Changed to string to allow uppercase mapping
    amount: number;
    description: string;
    start_date: string; // Added start_date
}

export interface SimulationResult {
    recommendation: 'Safe' | 'Caution' | 'Avoid';
    confidence: number;
    explanation: string;
    projected_impact: {
        lowest_balance: number;
        months_affected: number;
        total_cost: number;
    }
}

// Hooks

// Hardcoded User ID for MVP/Demo
const DEMO_USER_ID = "550e8400-e29b-41d4-a716-446655440000";
const DEMO_ACCOUNT_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11";

export const useUploadTransactions = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (file: File) => {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('account_id', DEMO_ACCOUNT_ID); // Required by backend

            // user_id is a Query param, not path param
            const response = await api.post(`/transactions/upload-csv?user_id=${DEMO_USER_ID}`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['cashflow'] });
            queryClient.invalidateQueries({ queryKey: ['forecast'] });
        },
    });
};

export const useCashflow = () => {
    return useQuery({
        queryKey: ['cashflow'],
        queryFn: async () => {
            const response = await api.get<CashflowData[]>(`/analytics/cashflow/${DEMO_USER_ID}`);
            return response.data;
        },
    });
};

export const useForecast = () => {
    return useQuery({
        queryKey: ['forecast'],
        queryFn: async () => {
            const response = await api.get<ForecastData[]>(`/analytics/forecast/${DEMO_USER_ID}`);
            return response.data;
        },
    });
};

export const useRunSimulation = () => {
    return useMutation({
        mutationFn: async (data: Omit<SimulationRequest, 'user_id' | 'start_date'> & { decision_type: 'one_time' | 'recurring' }) => {
            // Map frontend types to backend requirements
            const payload: SimulationRequest = {
                ...data,
                user_id: DEMO_USER_ID,
                start_date: new Date().toISOString().split('T')[0], // Default to today
                decision_type: data.decision_type.toUpperCase() // Ensure uppercase for backend enum
            };
            const response = await api.post<SimulationResult>('/simulation/run', payload);
            return response.data;
        }
    });
}
