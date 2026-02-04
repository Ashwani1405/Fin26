'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { LayoutDashboard, UploadCloud, TrendingUp, BrainCircuit } from 'lucide-react';

export function Navbar() {
    const pathname = usePathname();

    const links = [
        { href: '/', label: 'Upload', icon: UploadCloud },
        { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { href: '/forecast', label: 'Forecast', icon: TrendingUp },
        { href: '/simulate', label: 'Scenarios', icon: BrainCircuit },
    ];

    return (
        <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 items-center">
                <div className="mr-4 hidden md:flex">
                    <Link href="/" className="mr-6 flex items-center space-x-2">
                        <span className="hidden font-bold sm:inline-block">AI Personal CFO</span>
                    </Link>
                    <div className="flex gap-6 text-sm">
                        {/* Add breadcrumbs or secondary nav here if needed */}
                    </div>
                </div>
                <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                    <div className="w-full flex-1 md:w-auto md:flex-none">
                        <div className="flex items-center gap-2">
                            {links.map(({ href, label, icon: Icon }) => (
                                <Link key={href} href={href}>
                                    <Button
                                        variant={pathname === href ? 'default' : 'ghost'}
                                        size="sm"
                                        className={cn("gap-2", pathname === href && "bg-primary text-primary-foreground")}
                                    >
                                        <Icon className="h-4 w-4" />
                                        {label}
                                    </Button>
                                </Link>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
}
