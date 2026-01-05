import React, { useState, useEffect } from 'react';

const WalletAndCommissions = () => {
    const [walletInfo, setWalletInfo] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchWalletInfo = async () => {
            const token = localStorage.getItem('token');
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/wallet`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setWalletInfo(data);
            } else {
                console.error('Failed to fetch wallet info');
            }
            setLoading(false);
        };
        fetchWalletInfo();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (!walletInfo) {
        return <div className="text-center text-neutral-500">Could not load wallet information.</div>;
    }

    return (
        <div>
            <h2 className="text-3xl font-bold text-neutral-800 mb-6">Wallet & Commissions</h2>
            
            <div className="card-base mb-8 max-w-sm">
                <p className="text-sm font-medium text-neutral-500 uppercase">Balance</p>
                <p className="text-4xl font-bold text-neutral-800">${walletInfo.balance.toFixed(2)}</p>
                <p className="text-sm text-neutral-400 mt-1">This is the remaining balance after commission deductions.</p>
            </div>

            <h3 className="text-2xl font-bold text-neutral-800 mb-4">Commission History</h3>
            <div className="card-base overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-neutral-600">
                        <thead className="text-xs text-neutral-800 uppercase bg-neutral-100">
                            <tr>
                                <th scope="col" className="px-6 py-3">Amount</th>
                                <th scope="col" className="px-6 py-3">Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
                            {walletInfo.commission_ledgers.map((entry, index) => (
                                <tr key={index} className="bg-white border-b hover:bg-neutral-50">
                                    <td className="px-6 py-4 font-medium text-neutral-900">${entry.amount.toFixed(2)}</td>
                                    <td className="px-6 py-4">{new Date(entry.timestamp).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                 {walletInfo.commission_ledgers.length === 0 && (
                    <p className="text-center p-8 text-neutral-500">No commission history found.</p>
                )}
            </div>
        </div>
    );
};

export default WalletAndCommissions;
