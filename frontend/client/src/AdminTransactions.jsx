import React, { useState, useEffect } from 'react';

const AdminTransactions = () => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTransactions = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/transactions`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setTransactions(data);
                } else {
                    console.error('Failed to fetch transactions:', response.status, response.statusText);
                    // Optionally, show a user-friendly error message
                }
            } catch (error) {
                console.error('Network error fetching transactions:', error);
                // Optionally, show a user-friendly error message
            } finally {
                setLoading(false);
            }
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
                    <table className="table-base"> {/* Apply the new table-base class */}
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Amount</th>
                                <th>Phone</th>
                                <th>Status</th>
                                <th>Timestamp</th>
                                <th>Business ID</th>
                            </tr>
                        </thead>
                        <tbody>
                            {transactions.length > 0 ? (
                                transactions.map(tx => (
                                    <tr key={tx.id}>
                                        <td className="font-bold text-neutral-900">{tx.id}</td>
                                        <td>${tx.amount ? tx.amount.toFixed(2) : '0.00'}</td>
                                        <td>{tx.phone_number}</td>
                                        <td>
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                                tx.status === 'success' ? 'bg-success-100 text-success-800' :
                                                tx.status === 'pending' ? 'bg-neutral-200 text-neutral-800' : // Using neutral for pending
                                                'bg-error-100 text-error-800'
                                            }`}>
                                                {tx.status}
                                            </span>
                                        </td>
                                        <td>{new Date(tx.timestamp).toLocaleString()}</td>
                                        <td>{tx.business_id}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="6" className="text-center p-8 text-neutral-500">No transactions found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminTransactions;
