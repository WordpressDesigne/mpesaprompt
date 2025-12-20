import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';

const Dashboard = () => {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }

            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/dashboard`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUser(data);
            } else {
                // Token might be expired or invalid
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        fetchUserData();
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const businessNav = (
        <ul>
            <li className="p-4 hover:bg-gray-200"><a href="/dashboard">Home</a></li>
            <li className="p-4 hover:bg-gray-200"><a href="/dashboard/stk-push">Send STK Push</a></li>
            <li className="p-4 hover:bg-gray-200"><a href="/dashboard/customers">Customers</a></li>
            <li className="p-4 hover:bg-gray-200"><a href="/dashboard/wallet">Wallet & Commissions</a></li>
            <li className="p-4 hover:bg-gray-200"><a href="/dashboard/settings">Settings</a></li>
        </ul>
    );

    const adminNav = (
        <ul>
            <li className="p-4 hover:bg-gray-200"><a href="/dashboard">Home</a></li>
            <li className="p-4 hover:bg-gray-200"><a href="/admin/businesses">Manage Businesses</a></li>
            <li className="p-4 hover:bg-gray-200"><a href="/admin/transactions">All Transactions</a></li>
            <li className="p-4 hover:bg-gray-200"><a href="/admin/commissions">All Commissions</a></li>
        </ul>
    );

    return (
        <div className="flex h-screen bg-gray-100">
            <div className="w-64 bg-white shadow-md flex flex-col">
                <div className="p-4">
                    <h1 className="text-2xl font-bold">Dashboard</h1>
                    {user && <span className="text-sm text-gray-500">{user.role}</span>}
                </div>
                <nav className="flex-grow">
                    {user && (user.role === 'admin' ? adminNav : businessNav)}
                </nav>
                <div className="p-4">
                    <button onClick={handleLogout} className="w-full bg-gray-500 text-white p-2 rounded">
                        Logout
                    </button>
                </div>
            </div>
            <div className="flex-1 p-8 overflow-y-auto">
                <Outlet />
            </div>
        </div>
    );
};

export default Dashboard;
