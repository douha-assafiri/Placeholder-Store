import { useState, type SubmitEvent } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, UserRound } from 'lucide-react'
import { money } from '../data/products'
import { useStore } from '../context/useStore'
import { formText } from '../lib/form'

const errorText = (error: unknown) => (error instanceof Error ? error.message : 'Something went wrong')

export default function AccountPage() {
    const { user } = useStore()
    return (
        <main className="container page-space">
            <div className="account-wrap">
                <div className="account-art">
                    <span className="eyebrow">WELCOME TO PLACEHOLDER</span>
                    <h1>Good to<br /><em>see you.</em></h1>
                    <p>Your favourites, your orders, your corner of the store.</p>
                    <div className="account-art-bottom">Objects for living well.</div>
                </div>
                <div className="account-form">
                    <div className="account-symbol"><UserRound size={25} /></div>
                    {user ? <AccountDetails /> : <SignIn />}
                    <Link to="/shop" className="continue-shopping">Continue shopping</Link>
                </div>
            </div>
        </main>
    )
}

function SignIn() {
    const { login, register } = useStore()
    const [isRegister, setRegister] = useState(false)
    const [message, setMessage] = useState('')
    const [busy, setBusy] = useState(false)
    const submit = async (e: SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()
        const form = new FormData(e.currentTarget)
        const email = formText(form, 'email')
        const password = formText(form, 'password')
        setBusy(true)
        setMessage('')
        try {
            if (isRegister) {
                await register({ name: formText(form, 'name'), email, password, dob: formText(form, 'dob') })
            } else {
                await login(email, password)
            }
        } catch (error) {
            setMessage(errorText(error))
        } finally {
            setBusy(false)
        }
    }
    return (
        <>
            <span className="eyebrow">YOUR ACCOUNT</span>
            <h2>{isRegister ? 'Create an account' : 'Welcome back'}</h2>
            <p>{isRegister ? 'Join us to discover more.' : 'Sign in to continue your shopping journey.'}</p>
            <form onSubmit={submit}>
                {isRegister && <label>Full name<input name="name" required placeholder="Your name" /></label>}
                <label>Email address<input name="email" required type="email" placeholder="you@example.com" /></label>
                <label>Password<input name="password" required type="password" minLength={6} placeholder="At least 6 characters" /></label>
                {isRegister && <label>Date of birth<input name="dob" required type="date" /></label>}
                <button type="submit" className="btn btn-dark btn-full" disabled={busy}>
                    {isRegister ? 'Create account' : 'Sign in'} <ArrowRight size={18} />
                </button>
            </form>
            {message && <div className="demo-notice">{message}</div>}
            <p className="account-switch">
                {isRegister ? 'Already have an account?' : 'New around here?'}
                <button type="button" onClick={() => { setRegister(!isRegister); setMessage('') }}>
                    {isRegister ? 'Sign in' : 'Create an account'}
                </button>
            </p>
        </>
    )
}

function AccountDetails() {
    const { user, orders, isStaff, logout, updateProfile, changePassword, deleteAccount } = useStore()
    const [message, setMessage] = useState('')
    if (!user) return null

    const run = async (action: () => Promise<void>, done: string) => {
        setMessage('')
        try {
            await action()
            setMessage(done)
        } catch (error) {
            setMessage(errorText(error))
        }
    }
    const saveProfile = (e: SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()
        const form = new FormData(e.currentTarget)
        void run(() => updateProfile({
            name: formText(form, 'name'),
            email: formText(form, 'email'),
            dob: formText(form, 'dob'),
        }), 'Profile updated.')
    }
    const savePassword = (e: SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()
        const formElement = e.currentTarget
        const form = new FormData(formElement)
        void run(async () => {
            await changePassword(formText(form, 'old_password'), formText(form, 'new_password'))
            formElement.reset()
        }, 'Password changed.')
    }
    const remove = () => {
        if (window.confirm('Delete your account? This cannot be undone.')) void run(deleteAccount, '')
    }

    return (
        <>
            <span className="eyebrow">{isStaff ? 'STAFF ACCOUNT' : 'YOUR ACCOUNT'}</span>
            <h2>Hi, {user.name}</h2>
            <p>{user.email}</p>
            {isStaff && <p><Link to="/admin">Go to the admin dashboard <ArrowRight size={14} /></Link></p>}
            {message && <div className="demo-notice">{message}</div>}

            <h3>My orders</h3>
            {orders.length === 0
                ? <p>No orders yet.</p>
                : orders.map(order => (
                    <div className="success-order" key={order.id}>
                        <span>Order {order.id} · {order.date} · {order.status}</span>
                        <strong>{money(order.total)}</strong>
                    </div>
                ))}

            <h3>Profile</h3>
            <form onSubmit={saveProfile}>
                <label>Full name<input name="name" required defaultValue={user.name} /></label>
                <label>Email address<input name="email" required type="email" defaultValue={user.email} /></label>
                <label>Date of birth<input name="dob" required type="date" defaultValue={user.dob.slice(0, 10)} /></label>
                <button type="submit" className="btn btn-dark btn-full">Save profile</button>
            </form>

            <h3>Change password</h3>
            <form onSubmit={savePassword}>
                <label>Current password<input name="old_password" required type="password" /></label>
                <label>New password<input name="new_password" required type="password" minLength={6} /></label>
                <button type="submit" className="btn btn-dark btn-full">Change password</button>
            </form>

            <p className="account-switch">
                <button type="button" onClick={() => void run(logout, '')}>Sign out</button>
                <button type="button" onClick={remove}>Delete account</button>
            </p>
        </>
    )
}
