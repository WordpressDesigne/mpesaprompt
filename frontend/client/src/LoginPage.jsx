import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');

        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            navigate('/dashboard');
        } else if (response.status === 404) {
            navigate('/signup', { state: { email: email } });
        } else {
            setError('Login failed. Please check your credentials.');
        }
    };

    return (
        <div className="min-h-screen bg-neutral-100 flex flex-col justify-center items-center p-4">
            <div className="w-full max-w-md">
                <div className="card-base text-center">
                    <h1 className="text-3xl font-bold text-neutral-800 mb-2">Welcome Back!</h1>
                    <p className="text-neutral-600 mb-8">Log in to your MpesaPrompt account.</p>
                    
                    {error && <p className="bg-error-500 text-white p-3 rounded-lg mb-4">{error}</p>}

                    <form onSubmit={handleLogin} className="space-y-6 text-left">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-neutral-600 mb-1">Email</label>
                            <input
                                id="email"
                                type="email"
                                className="input-base"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-neutral-600 mb-1">Password</label>
                            <input
                                id="password"
                                type="password"
                                className="input-base"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <button type="submit" className="btn-primary w-full">
                            Login
                        </button>
                    </form>
                </div>
                <div className="text-center mt-6">
                    <p className="text-neutral-600">
                        Don't have an account? <Link to="/signup" className="font-medium text-primary-500 hover:underline">Sign up</Link>
                    </p>
                    <p className="text-sm text-neutral-400 mt-2">
                        or log in as <Link to="/admin/login" className="text-neutral-600 hover:underline">Admin</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
