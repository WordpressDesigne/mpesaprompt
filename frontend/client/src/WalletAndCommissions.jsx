import React, { useState, useEffect } from 'react';

const WalletAndCommissions = () => {
    const [walletInfo, setWalletInfo] = useState(null);

    useEffect(() => {
        const fetchWalletInfo = async () => {
            const token = localStorage.getItem('token');
            const response = await fetch('/wallet', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setWalletInfo(data);
            } else {
                console.error('Failed to fetch wallet info');
            }
        };
        fetchWalletInfo();
    }, []);

    if (!walletInfo) {
        return <div>Loading wallet information...</div>;
    }

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">Wallet & Commissions</h2>
            <div className="mb-4">
                <h3 className="text-xl font-semibold">Current Balance: ${walletInfo.balance.toFixed(2)}</h3>
            </div>
            <div>
                <h3 className="text-xl font-semibold mb-2">Commission Deductions</h3>
                <table className="min-w-full bg-white">
                    <thead>
                        <tr>
                            <th className="py-2">Amount</th>
                            <th className="py-2">Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        {walletInfo.commission_ledgers.map((entry, index) => (
                            <tr key={index}>
                                <td className="border px-4 py-2">{entry.amount.toFixed(2)}</td>
                                <td className="border px-4 py-2">{entry.timestamp}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default WalletAndCommissions;
