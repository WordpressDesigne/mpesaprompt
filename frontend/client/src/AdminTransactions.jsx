import React, { useState, useEffect } from 'react';

const AdminTransactions = () => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTransactions = async () => {
            const token = localStorage.getItem('token');
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/transactions`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setTransactions(data);
            } else {
                console.error('Failed to fetch transactions');
            }
            setLoading(false);
        };
        fetchTransactions();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2 className="text-3xl font-bold text-neutral-800 mb-6">All Transactions</h2>
            <div className="card-base overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-neutral-600">
                        <thead className="text-xs text-neutral-800 uppercase bg-neutral-100">
                            <tr>
                                <th scope="col" className="px-6 py-3">ID</th>
                                <th scope="col" className="px-6 py-3">Amount</th>
                                <th scope="col" className="px-6 py-3">Phone</th>
                                <th scope="col" className="px-6 py-3">Status</th>
                                <th scope="col" className="px-6 py-3">Timestamp</th>
                                <th scope="col" className="px-6 py-3">Business ID</th>
                            </tr>
                        </thead>
                        <tbody>
                            {transactions.map(tx => (
                                <tr key={tx.id} className="bg-white border-b hover:bg-neutral-50">
                                    <td className="px-6 py-4 font-bold text-neutral-900">{tx.id}</td>
                                    <td className="px-6 py-4">${tx.amount.toFixed(2)}</td>
                                    <td className="px-6 py-4">{tx.phone_number}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                            tx.status === 'success' ? 'bg-green-100 text-green-800' :
                                            tx.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                            'bg-red-100 text-red-800'
                                        }`}>
                                            {tx.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">{new Date(tx.timestamp).toLocaleString()}</td>
                                    <td className="px-6 py-4">{tx.business_id}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {transactions.length === 0 && (
                    <p className="text-center p-8 text-neutral-500">No transactions found.</p>
                )}
            </div>
        </div>
    );
};

export default AdminTransactions;
