import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle global errors here if needed (e.g. logging, toasts)
        console.error('API Error Details:', {
            status: error.response?.status,
            data: error.response?.data,
            message: error.message,
            url: error.config?.url
        });
        return Promise.reject(error);
    }
);
