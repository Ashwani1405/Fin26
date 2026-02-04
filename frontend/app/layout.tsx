import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { StoreProvider } from "@/components/providers/StoreProvider";
import { Toaster } from "@/components/ui/sonner";
import { cn } from "@/lib/utils";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "AI Personal CFO",
  description: "Financial modeling and decision support system.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={cn("min-h-screen bg-background font-sans antialiased", inter.variable)}>
        <Providers>
          <StoreProvider>
            {children}
            <Toaster />
          </StoreProvider>
        </Providers>
      </body>
    </html>
  );
}
