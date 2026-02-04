import { createStore } from 'zustand';
import { CashflowData, ForecastData } from './queries';
import { api } from './api'; // Import API client

// Hardcoded for MVP
const DEMO_USER_ID = "550e8400-e29b-41d4-a716-446655440000";

export type AppState = "EMPTY" | "UPLOADED" | "ANALYZED" | "FORECAST_READY";

export interface FinanceStore {
    // State
    appState: AppState;
    hasUploadedData: boolean;
    isLoading: boolean; // Add loading state
    error: string | null; // Add error state

    // Data Ownership
    monthlyCashflowData: CashflowData[];
    forecastData: ForecastData[];

    // Metadata
    availableDateRange: { minDate: string | null; maxDate: string | null };

    // Active Filter
    dateRange: { start: Date | null; end: Date | null };

    // Actions
    setUploadedData: (cashflow: CashflowData[]) => void;
    setForecastData: (forecast: ForecastData[]) => void;
    setDateRange: (range: { start: Date | null; end: Date | null }) => void;
    reset: () => void;

    // Async Hydration
    fetchMonthlyCashflow: () => Promise<void>;
    fetchForecastData: () => Promise<void>;
}

export const createFinanceStore = (initState: Partial<FinanceStore> = {}) => {
    return createStore<FinanceStore>((set, get) => ({
        appState: "EMPTY",
        hasUploadedData: false,
        isLoading: false,
        error: null,

        monthlyCashflowData: [],
        forecastData: [],

        availableDateRange: { minDate: null, maxDate: null },
        dateRange: { start: null, end: null },

        ...initState,

        setUploadedData: (cashflow) => {
            const dates = cashflow.map(c => c.month);
            const minDate = dates.length > 0 ? dates.sort()[0] : null;
            const maxDate = dates.length > 0 ? dates.sort()[dates.length - 1] : null;

            set({
                appState: "UPLOADED",
                hasUploadedData: true,
                monthlyCashflowData: cashflow,
                availableDateRange: { minDate, maxDate }
            });
        },

        setForecastData: (forecast) => {
            set({
                appState: "FORECAST_READY",
                forecastData: forecast
            });
        },

        setDateRange: (range) => set({ dateRange: range }),

        fetchMonthlyCashflow: async () => {
            set({ isLoading: true, error: null });
            try {
                const response = await api.get(`/analytics/cashflow/${DEMO_USER_ID}`);
                get().setUploadedData(response.data);
            } catch (err) {
                console.error("Failed to fetch cashflow:", err);
                set({ error: "Failed to load data. Please try again." });
            } finally {
                set({ isLoading: false });
            }
        },

        fetchForecastData: async () => {
            set({ isLoading: true, error: null });
            try {
                const response = await api.get(`/analytics/forecast/${DEMO_USER_ID}`);
                // Handle different response structures if needed, reusing validation logic or keeping it simple
                // Assuming service/schema fix made it consistent now
                if (response.data && Array.isArray(response.data.data_points)) {
                    get().setForecastData(response.data.data_points);
                } else if (Array.isArray(response.data)) {
                    get().setForecastData(response.data);
                } else {
                    console.error("Invalid forecast format in store fetch");
                }
            } catch (err) {
                console.error("Failed to fetch forecast:", err);
                set({ error: "Failed to generate forecast." });
            } finally {
                set({ isLoading: false });
            }
        },

        reset: () => set({
            appState: "EMPTY",
            hasUploadedData: false,
            monthlyCashflowData: [],
            forecastData: [],
            availableDateRange: { minDate: null, maxDate: null },
            dateRange: { start: null, end: null },
            error: null,
            isLoading: false
        })
    }));
};
