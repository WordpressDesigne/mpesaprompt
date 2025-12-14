import React from 'react';
import { Outlet } from 'react-router-dom';

const Dashboard = () => {
    return (
        <div className="flex h-screen bg-gray-100">
            <div className="w-64 bg-white shadow-md">
                <div className="p-4">
                    <h1 className="text-2xl font-bold">Dashboard</h1>
                </div>
                <nav>
                    <ul>
                        <li className="p-4 hover:bg-gray-200"><a href="/dashboard">Home</a></li>
                        <li className="p-4 hover:bg-gray-200"><a href="/dashboard/stk-push">Send STK Push</a></li>
                        <li className="p-4 hover:bg-gray-200"><a href="/dashboard/transactions">Transactions</a></li>
                        <li className="p-4 hover:bg-gray-200"><a href="/dashboard/customers">Customers</a></li>
                        <li className="p-4 hover:bg-gray-200"><a href="/dashboard/wallet">Wallet & Commissions</a></li>
                        <li className="p-4 hover
bg-gray-200"><a href="/dashboard/settings">Settings</a></li>
                    </ul>
                </nav>
            </div>
            <div className="flex-1 p-8">
                <Outlet />
            </div>
        </div>
    );
};

export default Dashboard;
