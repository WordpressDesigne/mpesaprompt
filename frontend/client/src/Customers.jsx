import React, { useState, useEffect } from 'react';

const Customers = () => {
    const [customers, setCustomers] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchCustomers = async () => {
            const token = localStorage.getItem('token');
            const response = await fetch('/customers', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
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
        customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        customer.phone_number.includes(searchTerm)
    );

    const handleExport = async () => {
        const token = localStorage.getItem('token');
        const response = await fetch('/customers/export-excel', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(new Blob([blob]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'customers.xlsx');
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } else {
            console.error('Failed to export customers to Excel');
        }
    };

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">Customers</h2>
            <div className="mb-4">
                <input
                    type="text"
                    placeholder="Search by name or phone number"
                    className="w-full p-2 border border-gray-300 rounded"
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                />
            </div>
            <button
                className="bg-green-500 text-white p-2 rounded mb-4"
                onClick={handleExport}
            >
                Export to Excel
            </button>
            <table className="min-w-full bg-white">
                <thead>
                    <tr>
                        <th className="py-2">Name</th>
                        <th className="py-2">Phone Number</th>
                        <th className="py-2">Total Amount Requested</th>
                        <th className="py-2">Transaction Count</th>
                        <th className="py-2">First Transaction</th>
                        <th className="py-2">Last Transaction</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredCustomers.map(customer => (
                        <tr key={customer.phone_number}>
                            <td className="border px-4 py-2">{customer.name}</td>
                            <td className="border px-4 py-2">{customer.phone_number}</td>
                            <td className="border px-4 py-2">{customer.total_amount_requested}</td>
                            <td className="border px-4 py-2">{customer.transaction_count}</td>
                            <td className="border px-4 py-2">{customer.first_transaction_date}</td>
                            <td className="border px-4 py-2">{customer.last_transaction_date}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Customers;
