import React, { useState, useEffect } from 'react';

const Customers = () => {
    const [customers, setCustomers] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchCustomers = async () => {
            const token = localStorage.getItem('token');
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/customers`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setCustomers(data);
            } else {
                console.error('Failed to fetch customers');
            }
        };
        fetchCustomers();
    }, []);

    const filteredCustomers = customers.filter(customer =>
        (customer.name && customer.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        customer.phone_number.includes(searchTerm)
    );

    const handleExport = async () => {
        // ... (export logic remains the same)
    };

    return (
        <div>
            <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
                <h2 className="text-3xl font-bold text-neutral-800">Customers</h2>
                <div className="w-full md:w-auto flex flex-col md:flex-row gap-4">
                     <input
                        type="text"
                        placeholder="Search..."
                        className="input-base w-full md:w-64"
                        value={searchTerm}
                        onChange={e => setSearchTerm(e.target.value)}
                    />
                    <button
                        className="btn-primary !bg-secondary-500 hover:!bg-green-600"
                        onClick={handleExport}
                    >
                        Export to Excel
                    </button>
                </div>
            </div>
            <div className="card-base overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-neutral-600">
                        <thead className="text-xs text-neutral-800 uppercase bg-neutral-100">
                            <tr>
                                <th scope="col" className="px-6 py-3">Name</th>
                                <th scope="col" className="px-6 py-3">Phone Number</th>
                                <th scope="col" className="px-6 py-3">Total Spent</th>
                                <th scope="col" className="px-6 py-3">Transactions</th>
                                <th scope="col" className="px-6 py-3">Last Active</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredCustomers.map(customer => (
                                <tr key={customer.phone_number} className="bg-white border-b hover:bg-neutral-50">
                                    <td className="px-6 py-4 font-medium text-neutral-900 whitespace-nowrap">{customer.name || '-'}</td>
                                    <td className="px-6 py-4">{customer.phone_number}</td>
                                    <td className="px-6 py-4">${customer.total_amount_requested.toFixed(2)}</td>
                                    <td className="px-6 py-4">{customer.transaction_count}</td>
                                    <td className="px-6 py-4">{customer.last_transaction_date ? new Date(customer.last_transaction_date).toLocaleDateString() : '-'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                 {filteredCustomers.length === 0 && (
                    <p className="text-center p-8 text-neutral-500">No customers found.</p>
                )}
            </div>
        </div>
    );
};

export default Customers;
