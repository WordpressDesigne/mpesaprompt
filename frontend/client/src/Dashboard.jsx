import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, Link, useLocation } from 'react-router-dom';

// Simple SVG icons for navigation
const HomeIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>;
const BusinessIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>;
const TransactionIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>;
const CommissionIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v.01" /></svg>;
const StkPushIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>;
const CustomersIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>;
const WalletIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>;
const SettingsIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.096 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>;
const LogoutIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>;
const MenuIcon = ({ className }) => <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>;


const NavLink = ({ to, icon, children }) => {
    const location = useLocation();
    const isActive = location.pathname === to;
    const iconClasses = "h-6 w-6"; // Define icon classes here

    return (
        <li>
            <Link 
                to={to} 
                className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                    isActive 
                        ? 'bg-primary-500 text-white shadow-md' 
                        : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                }`}
            >
                {React.cloneElement(icon, { className: iconClasses })}
                <span className="font-medium">{children}</span>
            </Link>
        </li>
    );
};

const Dashboard = () => {
    const [user, setUser] = useState(null);
    const [isSidebarOpen, setSidebarOpen] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }

            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/dashboard`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    setUser(data);
                } else {
                    localStorage.removeItem('token');
                    navigate('/login');
                }
            } catch (error) {
                console.error("Failed to fetch user data:", error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        fetchUserData();
    }, [navigate, location.pathname]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const businessNavLinks = [
        { to: "/dashboard/stk-push", icon: <StkPushIcon />, label: "Send STK Push" },
        { to: "/dashboard/customers", icon: <CustomersIcon />, label: "Customers" },
        { to: "/dashboard/wallet", icon: <WalletIcon />, label: "Wallet" },
        { to: "/dashboard/settings", icon: <SettingsIcon />, label: "Settings" },
    ];

    const adminNavLinks = [
        { to: "/dashboard/businesses", icon: <BusinessIcon />, label: "Businesses" },
        { to: "/dashboard/transactions", icon: <TransactionIcon />, label: "Transactions" },
        { to: "/dashboard/commissions", icon: <CommissionIcon />, label: "Commissions" },
        { to: "/dashboard/admin-settings", icon: <SettingsIcon />, label: "Admin Settings" }, // Example admin setting link
    ];

    const navLinks = user?.role === 'admin' ? adminNavLinks : businessNavLinks;

    const SidebarContent = () => (
        <div className="flex flex-col h-full bg-white text-neutral-800 border-r border-neutral-200">
            <div className="p-5 border-b border-neutral-200 flex items-center space-x-3">
                <Link to="/dashboard" className="flex items-center space-x-2">
                    <img src="/vite.svg" alt="MpesaPrompt Logo" className="h-8 w-8" /> {/* Placeholder for a proper logo */}
                    <h1 className="text-xl font-extrabold text-primary-600">MpesaPrompt</h1>
                </Link>
            </div>
            <div className="p-4 text-center">
                {user && (
                    <>
                        <p className="text-lg font-semibold text-neutral-800">{user.name || user.email}</p>
                        <p className="text-sm text-neutral-500 capitalize">{user.role} Dashboard</p>
                    </>
                )}
            </div>
            <nav className="flex-grow p-4">
                <ul className="space-y-2">
                    <NavLink to="/dashboard" icon={<HomeIcon />}>Home</NavLink>
                    {navLinks.map(link => <NavLink key={link.to} {...link}>{link.label}</NavLink>)}
                </ul>
            </nav>
            <div className="p-4 border-t border-neutral-200">
                <button onClick={handleLogout} className="btn-secondary w-full flex items-center justify-center space-x-3 hover:bg-red-500 hover:text-white">
                    <LogoutIcon className="h-6 w-6" />
                    <span className="font-medium">Logout</span>
                </button>
            </div>
        </div>
    );

    return (
        <div className="relative min-h-screen bg-neutral-50 flex">
            {/* Mobile menu button and header */}
            <header className="bg-white shadow-sm p-4 flex justify-between items-center md:hidden w-full z-10">
                <Link to="/dashboard" className="flex items-center space-x-2">
                    <img src="/vite.svg" alt="MpesaPrompt Logo" className="h-7 w-7" />
                    <h1 className="text-lg font-extrabold text-primary-600">MpesaPrompt</h1>
                </Link>
                <button onClick={() => setSidebarOpen(true)} className="p-2 rounded-md text-neutral-600 hover:bg-neutral-100 focus:outline-none focus:ring-2 focus:ring-neutral-200">
                    <MenuIcon className="h-6 w-6" />
                </button>
            </header>

            {/* Mobile menu overlay */}
            <div 
                className={`fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden ${isSidebarOpen ? 'block' : 'hidden'}`}
                onClick={() => setSidebarOpen(false)}
            ></div>
            
            {/* Sidebar */}
            <aside className={`fixed top-0 left-0 h-full w-64 bg-white shadow-lg transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out md:relative md:translate-x-0 md:flex-shrink-0 z-30`}>
                <SidebarContent />
            </aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col min-h-screen">
                <div className="flex-1 p-4 md:p-8 overflow-y-auto">
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
