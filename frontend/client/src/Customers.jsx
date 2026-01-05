import React, { useState, useEffect } from 'react';

const Customers = () => {
    const [customers, setCustomers] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchCustomers = async () => {
            const token = localStorage.getItem('token');
            // Error handling for fetch
            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/customers`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setCustomers(data);
                } else {
                    console.error('Failed to fetch customers:', response.status, response.statusText);
                    // Optionally, show a user-friendly error message
                }
            } catch (error) {
                console.error('Network error fetching customers:', error);
                // Optionally, show a user-friendly error message
            }
        };
        fetchCustomers();
    }, []);

    const filteredCustomers = customers.filter(customer =>
        (customer.name && customer.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (customer.phone_number && customer.phone_number.includes(searchTerm))
    );

    const handleExport = async () => {
        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/customers/export-excel`, {
                headers: { 'Authorization': `Bearer ${token}` }
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
                console.error('Failed to export customers:', response.status, response.statusText);
                // Optionally, show a user-friendly error message
            }
        } catch (error) {
            console.error('Network error exporting customers:', error);
            // Optionally, show a user-friendly error message
        }
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
                        className="btn-secondary" // Using the new btn-secondary class
                        onClick={handleExport}
                    >
                        Export to Excel
                    </button>
                </div>
            </div>
            <div className="card-base overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="table-base"> {/* Apply the new table-base class */}
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Phone Number</th>
                                <th>Total Spent</th>
                                <th>Transactions</th>
                                <th>Last Active</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredCustomers.length > 0 ? (
                                filteredCustomers.map(customer => (
                                    <tr key={customer.phone_number}>
                                        <td className="font-medium text-neutral-900 whitespace-nowrap">{customer.name || '-'}</td>
                                        <td>{customer.phone_number}</td>
                                        <td>${customer.total_amount_requested ? customer.total_amount_requested.toFixed(2) : '0.00'}</td>
                                        <td>{customer.transaction_count}</td>
                                        <td>{customer.last_transaction_date ? new Date(customer.last_transaction_date).toLocaleDateString() : '-'}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center p-8 text-neutral-500">No customers found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Customers;
