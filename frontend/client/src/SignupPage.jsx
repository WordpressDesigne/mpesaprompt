import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';

const SignupPage = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const location = useLocation();

    const isEmailPrefilled = !!location.state?.email;

    useEffect(() => {
        if (isEmailPrefilled) {
            setEmail(location.state.email);
        }
    }, [location.state]);

    const handleSignup = async (e) => {
        e.preventDefault();
        setError('');

        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password }),
        });

        if (response.ok) {
            navigate('/login');
        } else {
            const data = await response.json();
            setError(data.message || 'Signup failed. Please try again.');
        }
    };

    return (
        <div className="min-h-screen bg-neutral-100 flex flex-col justify-center items-center p-4">
            <div className="w-full max-w-md">
                <div className="card-base text-center">
                    <h1 className="text-3xl font-bold text-neutral-800 mb-2">Create an Account</h1>
                    <p className="text-neutral-600 mb-8">
                        {isEmailPrefilled
                            ? "Your business wasn't found. Let's get you set up!"
                            : "Start accepting payments with MpesaPrompt."}
                    </p>

                    {error && <p className="bg-error-500 text-white p-3 rounded-lg mb-4">{error}</p>}

                    <form onSubmit={handleSignup} className="space-y-6 text-left">
                        <div className="mb-4">
                            <label htmlFor="name" className="block text-sm font-medium text-neutral-600 mb-1">Business Name</label>
                            <input
                                id="name"
                                type="text"
                                className="input-base"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-neutral-600 mb-1">Email</label>
                            <input
                                id="email"
                                type="email"
                                className={`input-base ${isEmailPrefilled ? 'bg-neutral-100' : ''}`}
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                readOnly={isEmailPrefilled}
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
                            Create Account
                        </button>
                    </form>
                </div>
                <div className="text-center mt-6">
                    <p className="text-neutral-600">
                        Already have an account? <Link to="/login" className="font-medium text-primary-500 hover:underline">Log in</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default SignupPage;
