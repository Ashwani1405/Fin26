'use client';

import { type ReactNode, createContext, useRef, useContext } from 'react';
import { useStore } from 'zustand';
import { type FinanceStore, createFinanceStore } from '@/lib/store';

export type FinanceStoreApi = ReturnType<typeof createFinanceStore>;

export const FinanceStoreContext = createContext<FinanceStoreApi | undefined>(
    undefined,
);

export interface StoreProviderProps {
    children: ReactNode;
}

export const StoreProvider = ({ children }: StoreProviderProps) => {
    const storeRef = useRef<FinanceStoreApi>(null);
    if (!storeRef.current) {
        storeRef.current = createFinanceStore();
    }

    return (
        <FinanceStoreContext.Provider value={storeRef.current}>
            {children}
        </FinanceStoreContext.Provider>
    );
};

export const useFinanceStore = <T,>(
    selector: (store: FinanceStore) => T,
): T => {
    const financeStoreContext = useContext(FinanceStoreContext);

    if (!financeStoreContext) {
        throw new Error(`useFinanceStore must be used within StoreProvider`);
    }

    return useStore(financeStoreContext, selector);
};
