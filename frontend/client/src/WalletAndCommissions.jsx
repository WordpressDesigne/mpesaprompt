import React, { useState, useEffect } from 'react';

const WalletAndCommissions = () => {
    const [walletInfo, setWalletInfo] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchWalletInfo = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/wallet`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setWalletInfo(data);
                } else {
                    console.error('Failed to fetch wallet info:', response.status, response.statusText);
                    // Optionally, show a user-friendly error message
                }
            } catch (error) {
                console.error('Network error fetching wallet info:', error);
                // Optionally, show a user-friendly error message
            } finally {
                setLoading(false);
            }
        };
        fetchWalletInfo();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (!walletInfo) {
        return <div className="text-center text-neutral-500 p-8">Could not load wallet information. Please try again later.</div>;
    }

    return (
        <div>
            <h2 className="text-3xl font-bold text-neutral-800 mb-6">Wallet & Commissions</h2>
            
            <div className="card-base mb-8 max-w-sm">
                <p className="text-sm font-medium text-neutral-500 uppercase">Current Balance</p>
                <p className="text-4xl font-bold text-neutral-800">${walletInfo.balance ? walletInfo.balance.toFixed(2) : '0.00'}</p>
                <p className="text-sm text-neutral-400 mt-1">This is the remaining balance after commission deductions.</p>
            </div>

            <h3 className="text-2xl font-bold text-neutral-800 mb-4">Commission History</h3>
            <div className="card-base overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="table-base"> {/* Apply the new table-base class */}
                        <thead>
                            <tr>
                                <th>Amount</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
                            {walletInfo.commission_ledgers.length > 0 ? (
                                walletInfo.commission_ledgers.map((entry, index) => (
                                    <tr key={index}>
                                        <td className="font-medium text-neutral-900">${entry.amount ? entry.amount.toFixed(2) : '0.00'}</td>
                                        <td>{new Date(entry.timestamp).toLocaleString()}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="2" className="text-center p-8 text-neutral-500">No commission history found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default WalletAndCommissions;
