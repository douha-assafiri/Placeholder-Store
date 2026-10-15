import { Link, useParams } from 'react-router-dom'
import { CheckCircle2, ArrowRight } from 'lucide-react'
import { useStore } from '../context/useStore'
import { money } from '../data/products'

export default function OrderSuccessPage() {
    const { id } = useParams()
    const { orders } = useStore()
    const order = orders.find(o => o.id === id)
    return (
        <main className="container page-space">
            <div className="success-card">
                <CheckCircle2 size={58} />
                <span className="eyebrow">ORDER PLACED</span>
                <h1>Thanks for shopping with us.</h1>
                <p>Your order has been saved to your account. No payment was processed.</p>
                {order && (
                    <div className="success-order">
                        <span>Order {order.id} · {order.status}</span>
                        <strong>{money(order.total)}</strong>
                    </div>
                )}
                <Link className="btn btn-dark" to="/shop">Keep exploring <ArrowRight size={18} /></Link>
            </div>
        </main>
    )
}
