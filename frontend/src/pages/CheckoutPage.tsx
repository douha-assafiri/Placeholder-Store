import { useState, type SubmitEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, LockKeyhole } from 'lucide-react'
import { money } from '../data/products'
import { useStore } from '../context/useStore'
import { formText } from '../lib/form'

export default function CheckoutPage() {
    const { cart, catalog, subtotal, placeOrder, user } = useStore()
    const navigate = useNavigate()
    const [busy, setBusy] = useState(false)
    const [message, setMessage] = useState('')
    const submit = async (e: SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()
        const form = new FormData(e.currentTarget)
        const field = (name: string) => formText(form, name)
        setBusy(true)
        setMessage('')
        try {
            const order = await placeOrder({
                first_name: field('first_name'),
                last_name: field('last_name'),
                email: field('email'),
                street: field('street'),
                city: field('city'),
                state: field('state'),
                postcode: field('postcode'),
                country: field('country'),
            })
            if (order) navigate(`/order-success/${order.id}`)
            else setBusy(false)
        } catch (error) {
            setMessage(error instanceof Error ? error.message : 'Could not place the order')
            setBusy(false)
        }
    }
    let content
    if (!cart.length) {
        content = (
            <div className="empty-state">
                <h2>Your bag is empty</h2>
                <Link className="btn btn-dark" to="/shop">
                    Shop products
                </Link>
            </div>
        )
    } else if (!user) {
        content = (
            <div className="empty-state">
                <h2>Sign in to check out</h2>
                <p>Your bag is saved while you sign in or create an account.</p>
                <Link className="btn btn-dark" to="/account">
                    Sign in
                </Link>
            </div>
        )
    } else {
        content = (
            <div className="checkout-layout">
                <form id="checkout-form" className="checkout-form" onSubmit={submit}>
                    <h2>Contact details</h2>
                    <div className="field-grid">
                        <label>First name<input name="first_name" required autoComplete="given-name" placeholder="First name" />
                        </label>
                        <label>Last name<input name="last_name" required autoComplete="family-name" placeholder="Last name" />
                        </label>
                    </div>
                    <label>Email address<input
                            name="email"
                            type="email"
                            required
                            autoComplete="email"
                            placeholder="you@example.com"
                            defaultValue={user.email}
                        />
                    </label>
                    <h2>Delivery address</h2>
                    <label>Street address<input name="street" required autoComplete="street-address" placeholder="123 Example Street" />
                    </label>
                    <div className="field-grid">
                        <label>Suburb / City<input name="city" required autoComplete="address-level2" placeholder="Melbourne" />
                        </label>
                        <label>State<input name="state" required autoComplete="address-level1" placeholder="VIC" />
                        </label>
                    </div>
                    <div className="field-grid">
                        <label>Postcode<input name="postcode" required inputMode="numeric" pattern="[0-9]{4}" placeholder="3000" />
                        </label>
                        <label>Country<select name="country" defaultValue="Australia">
                                <option>Australia</option>
                            </select>
                        </label>
                    </div>
                    <div className="demo-notice">
                        <LockKeyhole size={18} />
                        <span>Your order and delivery details are saved to your account. No payment is taken.</span>
                    </div>
                    {message && <div className="demo-notice">{message}</div>}
                </form>
                <aside className="summary-card">
                    <h2>Your order</h2>
                    {cart.map(item => {
                        const p = catalog.find(x => x.id === item.id)
                        return p ? (
                            <div className="checkout-item" key={item.id}>
                                <img src={p.image} alt="" />
                                <div>
                                    <strong>{p.name}</strong>
                                    <small>Qty {item.quantity}</small>
                                </div>
                                <span>{money(p.price * item.quantity)}</span>
                            </div>
                        ) : null
                    })}
                    <div className="summary-line summary-total">
                        <span>Total</span>
                        <strong>{money(subtotal)}</strong>
                    </div>
                    <button type="submit" form="checkout-form" disabled={busy} className="btn btn-dark btn-full">
                        Place order
                    </button>
                </aside>
            </div>
        )
    }
    return (
        <main className="container page-space">
            <Link to="/cart" className="back-link">
                <ArrowLeft size={16} /> Back to bag
            </Link>
            <div className="page-intro">
                <span className="eyebrow">ALMOST THERE</span>
                <h1>
                    Checkout<span className="accent-dot">.</span>
                </h1>
                <p>Enter your details to place your order. No payment is collected.</p>
            </div>
            {content}
        </main>
    )
}
