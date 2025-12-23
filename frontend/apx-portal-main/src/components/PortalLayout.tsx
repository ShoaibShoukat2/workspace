import React, { useRef, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import { LogOut, Sun, Moon, Settings, Upload, X, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import Button from '@/components/ui/Button'; // Assuming Button component exists

interface PortalLayoutProps {
    children: React.ReactNode;
    title: string;
    navItems?: Array<{ label: string; path: string; icon?: React.ReactNode }>;
}

export default function PortalLayout({ children, title, navItems }: PortalLayoutProps) {
    const navigate = useNavigate();
    const location = useLocation();
    const { currentUser, logout, updateUser } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const [activePath, setActivePath] = React.useState(location.pathname);
    const [showSettings, setShowSettings] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Update activePath whenever the location changes
    React.useEffect(() => {
        setActivePath(location.pathname);
    }, [location.pathname]);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const handleNavigate = (path: string) => {
        setActivePath(path);
        navigate(path);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const url = URL.createObjectURL(file);
            updateUser({ avatarUrl: url });
        }
    };

    const triggerFileUpload = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className="min-h-screen flex bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/30 dark:from-gray-900 dark:via-purple-950/30 dark:to-violet-950/30 smooth-transition">
            {/* Floating Island Sidebar */}
            <aside className="fixed left-6 top-6 bottom-6 z-50 w-16 hidden md:flex flex-col">
                <div className="flex-1 bg-gradient-to-b from-purple-600 via-purple-700 to-violet-800 dark:from-purple-700 dark:via-purple-800 dark:to-violet-900 rounded-[28px] shadow-island dark:shadow-island-dark p-3 flex flex-col items-center smooth-transition border border-white/10">
                    {/* Logo */}
                    <div className="mb-6 mt-1">
                        <div className="w-10 h-10 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-xl hover:bg-white/30 smooth-transition cursor-pointer group hover:rotate-12 hover:scale-110">
                            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-pink-400 to-purple-300 group-hover:scale-110 smooth-transition" />
                        </div>
                    </div>

                    {/* Navigation Icons */}
                    <nav className="flex-1 flex flex-col items-center space-y-3 py-4">
                        {navItems?.map((item, index) => (
                            <button
                                key={index}
                                onClick={() => handleNavigate(item.path)}
                                className={cn(
                                    'w-10 h-10 rounded-xl flex items-center justify-center smooth-transition relative group overflow-hidden',
                                    activePath === item.path
                                        ? 'bg-white text-purple-700 shadow-glow scale-110'
                                        : 'text-white/70 hover:text-white hover:bg-white/10 hover:scale-110 hover:shadow-glow-hover'
                                )}
                                title={item.label}
                            >
                                <div className="transform transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 group-hover:drop-shadow-lg">
                                    {item.icon}
                                </div>
                                {/* Tooltip */}
                                <div className="absolute left-full ml-4 px-3 py-1.5 bg-gray-900 dark:bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none smooth-transition whitespace-nowrap z-50 shadow-xl">
                                    {item.label}
                                    <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900 dark:border-r-gray-800" />
                                </div>
                            </button>
                        ))}
                    </nav>

                    {/* Bottom Actions */}
                    <div className="flex flex-col items-center space-y-3 mb-2">
                        {/* Settings Toggle */}
                        <button
                            onClick={() => setShowSettings(!showSettings)}
                            className={cn(
                                "w-10 h-10 rounded-xl flex items-center justify-center smooth-transition relative group",
                                showSettings ? "text-white bg-white/10" : "text-white/70 hover:text-white hover:bg-white/10 hover:scale-110"
                            )}
                            title="Settings"
                        >
                            <Settings className="w-5 h-5 transform transition-transform duration-300 group-hover:rotate-45" />
                        </button>

                        {/* Theme Toggle */}
                        <button
                            onClick={toggleTheme}
                            className="w-10 h-10 rounded-xl flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 hover:scale-110 smooth-transition relative group"
                            title={theme === 'light' ? 'Dark Mode' : 'Light Mode'}
                        >
                            <div className="transform transition-transform duration-200 group-hover:scale-110">
                                {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
                            </div>
                        </button>

                        {/* User Avatar */}
                        <div
                            className="relative group cursor-pointer hover:scale-105 smooth-transition"
                            onClick={() => setShowSettings(true)}
                        >
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 flex items-center justify-center text-white font-bold text-sm shadow-lg ring-2 ring-white/20 hover:ring-white/40 smooth-transition overflow-hidden">
                                {currentUser?.avatarUrl ? (
                                    <img src={currentUser.avatarUrl} alt={currentUser.name} className="w-full h-full object-cover" />
                                ) : (
                                    currentUser?.name?.charAt(0) || 'U'
                                )}
                            </div>
                        </div>

                        {/* Logout */}
                        <button
                            onClick={handleLogout}
                            className="w-10 h-10 rounded-xl flex items-center justify-center text-white/70 hover:text-red-300 hover:bg-red-500/20 hover:scale-110 smooth-transition relative group"
                            title="Logout"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 md:ml-28 relative">
                {/* Top Bar */}
                <header className="sticky top-0 z-40 backdrop-blur-xl bg-white/70 dark:bg-gray-900/70 border-b border-gray-200/50 dark:border-gray-700/50 px-6 md:px-8 py-4 smooth-transition">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl md:text-3xl font-bold gradient-text">
                                {title}
                            </h1>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5 capitalize">
                                {currentUser?.role} Dashboard
                            </p>
                        </div>

                        {/* Search Bar */}
                        <div className="flex-1 max-w-xl mx-8 hidden md:block">
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Search className="h-5 w-5 text-gray-400 group-focus-within:text-purple-500 smooth-transition" />
                                </div>
                                <input
                                    type="text"
                                    className="block w-full pl-10 pr-3 py-2 border border-gray-200 dark:border-gray-700 rounded-xl leading-5 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 focus:outline-none focus:bg-white dark:focus:bg-gray-900 focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 sm:text-sm smooth-transition"
                                    placeholder="Search for jobs, reports, or settings..."
                                />
                            </div>
                        </div>

                        {/* Desktop Header Actions */}
                        <div className="hidden md:flex items-center space-x-4">
                            {/* User Profile Pill */}
                            <div
                                className="flex items-center space-x-3 px-3 py-1.5 rounded-full bg-white/50 dark:bg-gray-800/50 border border-gray-200/50 dark:border-gray-700/50 hover:bg-white/80 dark:hover:bg-gray-800/80 cursor-pointer smooth-transition group"
                                onClick={() => setShowSettings(true)}
                            >
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-xs font-bold ring-2 ring-white/20 group-hover:ring-purple-400/50 smooth-transition overflow-hidden">
                                    {currentUser?.avatarUrl ? (
                                        <img src={currentUser.avatarUrl} alt={currentUser.name} className="w-full h-full object-cover" />
                                    ) : (
                                        currentUser?.name?.charAt(0) || 'U'
                                    )}
                                </div>
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-200 pr-2">
                                    {currentUser?.name}
                                </span>
                            </div>

                            <button
                                onClick={toggleTheme}
                                className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 smooth-transition group"
                            >
                                {theme === 'light' ? (
                                    <>
                                        <Moon className="w-4 h-4 text-gray-700 dark:text-gray-300 group-hover:scale-110 smooth-transition" />
                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Dark</span>
                                    </>
                                ) : (
                                    <>
                                        <Sun className="w-4 h-4 text-gray-300 group-hover:scale-110 smooth-transition" />
                                        <span className="text-sm font-medium text-gray-300">Light</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </header>

                {/* Settings Modal/Panel */}
                {showSettings && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in" onClick={() => setShowSettings(false)}>
                        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md p-6 m-4 border border-white/20 animate-scale-in" onClick={e => e.stopPropagation()}>
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Profile Settings</h2>
                                <button onClick={() => setShowSettings(false)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full smooth-transition">
                                    <X className="w-5 h-5 text-gray-500" />
                                </button>
                            </div>

                            <div className="flex flex-col items-center space-y-4 mb-6">
                                <div className="relative group">
                                    <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 p-1 ring-4 ring-purple-100 dark:ring-purple-900/30">
                                        <div className="w-full h-full rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center overflow-hidden">
                                            {currentUser?.avatarUrl ? (
                                                <img src={currentUser.avatarUrl} alt={currentUser.name} className="w-full h-full object-cover" />
                                            ) : (
                                                <span className="text-3xl font-bold text-gray-400">{currentUser?.name.charAt(0)}</span>
                                            )}
                                        </div>
                                    </div>
                                    <button
                                        onClick={triggerFileUpload}
                                        className="absolute bottom-0 right-0 p-2 rounded-full bg-purple-600 text-white shadow-lg hover:bg-purple-700 hover:scale-110 smooth-transition"
                                    >
                                        <Upload className="w-4 h-4" />
                                    </button>
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        className="hidden"
                                        accept="image/*"
                                        onChange={handleFileChange}
                                    />
                                </div>
                                <div className="text-center">
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{currentUser?.name}</h3>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">{currentUser?.role}</p>
                                </div>
                            </div>

                            <div className="space-y-3">
                                <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700/50">
                                    <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1 block">Email</label>
                                    <p className="text-gray-900 dark:text-gray-200">{currentUser?.email}</p>
                                </div>
                                {currentUser?.insuranceExpiryDate && (
                                    <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700/50">
                                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1 block">Insurance Expiry</label>
                                        <p className="text-gray-900 dark:text-gray-200">{currentUser.insuranceExpiryDate}</p>
                                    </div>
                                )}
                            </div>

                            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-800">
                                <Button className="w-full" onClick={() => setShowSettings(false)}>
                                    Done
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Page Content */}
                <main className="p-6 md:p-8">
                    <div className="max-w-7xl mx-auto">
                        {children}
                    </div>
                </main>
            </div>

            {/* Mobile Bottom Navigation - Island Style */}
            <nav className="md:hidden fixed bottom-6 left-4 right-4 z-50 bg-gradient-to-r from-purple-700 via-purple-800 to-violet-900 dark:from-purple-800 dark:via-purple-900 dark:to-violet-950 rounded-2xl shadow-xl shadow-purple-900/40 border border-white/10 backdrop-blur-xl px-2 py-2 smooth-transition animate-slide-up">
                <div className="flex items-center justify-around">
                    {navItems?.slice(0, 4).map((item, index) => (
                        <button
                            key={index}
                            onClick={() => handleNavigate(item.path)}
                            className={cn(
                                'flex flex-col items-center justify-center p-2 rounded-xl smooth-transition relative w-16',
                                activePath === item.path
                                    ? 'bg-white text-purple-700 shadow-md transform -translate-y-4 rounded-xl ring-4 ring-gray-100 dark:ring-gray-900'
                                    : 'text-white/70 hover:text-white'
                            )}
                        >
                            <div className={cn(
                                "transform transition-all duration-300",
                                activePath === item.path ? "scale-110" : "scale-100"
                            )}>
                                {item.icon}
                            </div>
                            {/* Label only if active or simple dot if not to save space? User wants consistency. Let's show label. */}
                            <span className={cn(
                                "text-[10px] font-bold mt-1 max-w-full truncate",
                                activePath === item.path ? "block" : "hidden sm:block"
                            )}>
                                {item.label.split(' ')[0]}
                            </span>
                        </button>
                    ))}
                    <button
                        onClick={() => setShowSettings(true)}
                        className="flex flex-col items-center justify-center p-2 rounded-xl smooth-transition text-white/70 w-16"
                    >
                        <Settings className="w-6 h-6" />
                    </button>
                </div>
            </nav>
        </div>
    );
}
