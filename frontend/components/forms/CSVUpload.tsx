'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useUploadTransactions, useCashflow, useForecast } from '@/lib/queries';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import Link from 'next/link';

export function CSVUpload() {
    const [uploadProgress, setUploadProgress] = useState(0);
    const { mutateAsync: upload, isPending, isSuccess, isError, error } = useUploadTransactions();

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (!file) return;

        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            toast.error('Please upload a CSV file.');
            return;
        }

        try {
            setUploadProgress(50); // Indeterminate progress
            // The mutationFn expects a File object directly
            await upload(file);
            setUploadProgress(100);
            toast.success('Transactions uploaded successfully!');
            // No auto-redirect. User will click "Go to Dashboard".
        } catch (e: any) {
            setUploadProgress(0);
            console.error("Upload failed", e);
            toast.error(e?.response?.data?.detail || "Failed to upload transactions.");
        }
    }, [upload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
        },
        maxFiles: 1,
        disabled: isPending || isSuccess,
    });

    return (
        <Card className="w-full max-w-xl mx-auto border-dashed border-2 shadow-sm hover:border-primary/50 transition-colors">
            <CardHeader>
                <CardTitle className="text-xl font-semibold text-center">Upload Transactions</CardTitle>
                <CardDescription className="text-center">
                    Drag and drop your bank statement CSV here.
                </CardDescription>
            </CardHeader>
            <CardContent>
                {/* Upload Area */}
                {!isSuccess && (
                    <div
                        {...getRootProps()}
                        className={cn(
                            "flex flex-col items-center justify-center p-10 rounded-lg cursor-pointer transition-all duration-200",
                            isDragActive ? "bg-primary/5 scale-[0.98]" : "bg-muted/30 hover:bg-muted/50",
                            (isPending) && "pointer-events-none opacity-50"
                        )}
                    >
                        <input {...getInputProps()} />

                        <div className="bg-background p-4 rounded-full shadow-sm mb-4">
                            {isError ? (
                                <AlertCircle className="h-8 w-8 text-destructive" />
                            ) : (
                                <UploadCloud className="h-8 w-8 text-primary" />
                            )}
                        </div>

                        <p className="text-sm font-medium text-muted-foreground mb-1">
                            {isDragActive ? "Drop the file here" : "Click to browse or drag file"}
                        </p>
                        <p className="text-xs text-muted-foreground/60">
                            Supports CSV files up to 10MB
                        </p>
                    </div>
                )}

                {isPending && (
                    <div className="mt-6 space-y-2">
                        <div className="flex justify-between text-xs text-muted-foreground">
                            <span>Uploading...</span>
                            <span>{uploadProgress}%</span>
                        </div>
                        <Progress value={uploadProgress} className="h-2" />
                    </div>
                )}

                {/* Success State with Manual Navigation */}
                {isSuccess && (
                    <div className="flex flex-col items-center justify-center py-8 space-y-4 animate-in fade-in zoom-in-50">
                        <div className="bg-green-100 dark:bg-green-900/30 p-4 rounded-full">
                            <CheckCircle2 className="h-12 w-12 text-green-600 dark:text-green-400" />
                        </div>
                        <div className="text-center space-y-1">
                            <h3 className="text-lg font-semibold">Upload Complete</h3>
                            <p className="text-muted-foreground text-sm">Your data is ready for analysis.</p>
                        </div>

                        <Button
                            className="w-full max-w-xs mt-4"
                            size="lg"
                            asChild
                        >
                            <Link href="/dashboard">Go to Dashboard</Link>
                        </Button>
                    </div>
                )}

                {isError && (
                    <div className="mt-6 text-center text-sm text-destructive font-medium animate-in fade-in slide-in-from-bottom-2">
                        {String(error) || "Upload failed. Please try again."}
                    </div>
                )}

            </CardContent>
        </Card>
    );
}
