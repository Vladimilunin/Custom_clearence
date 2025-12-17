'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
    const pathname = usePathname();

    const links = [
        {
            href: '/',
            label: 'Генератор',
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            )
        },
        {
            href: '/parts',
            label: 'База деталей',
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
            )
        },
    ];

    return (
        <aside className="w-64 fixed inset-y-0 left-0 z-50 flex flex-col bg-card border-r border-border transition-all duration-300">
            {/* Logo Area */}
            <div className="h-16 flex items-center px-6 border-b border-border">
                <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
                        G
                    </div>
                    <span className="font-semibold text-lg tracking-tight text-foreground">GenDocs</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-6 px-3 space-y-0.5">
                {links.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${isActive
                                    ? 'bg-secondary text-foreground'
                                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                                }`}
                        >
                            <span className={isActive ? 'text-foreground' : 'text-muted-foreground group-hover:text-foreground'}>
                                {link.icon}
                            </span>
                            {link.label}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer / User */}
            <div className="p-4 border-t border-border">
                <div className="flex items-center gap-3 p-2 rounded-md hover:bg-secondary/50 transition-colors cursor-pointer">
                    <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-xs font-medium text-foreground">
                        AD
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">Admin User</p>
                        <p className="text-xs text-muted-foreground truncate">admin@bsl-lab.ru</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}
