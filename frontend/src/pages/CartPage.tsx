import {Link} from 'react-router-dom'
import {ArrowRight, Minus, Plus, ShoppingBag, Trash2} from 'lucide-react'
import {money} from '../data/products'
import {useStore} from '../context/useStore'

export default function CartPage() {
    const {cart, catalog, remove, update, subtotal} = useStore();
    const plural = cart.length === 1 ? '' : 's';
    return <main className="container page-space">
        <div className="page-intro"><span className="eyebrow">YOUR SELECTION</span><h1>Shopping bag<span
            className="accent-dot">.</span></h1>
            <p>{cart.length ? `You've got ${cart.length} lovely find${plural} in your bag.` : 'Your next favourite is waiting to be discovered.'}</p>
        </div>
        {!cart.length ?
            <div className="empty-state"><ShoppingBag size={48}/><h2>Your bag is empty</h2><p>Start exploring our
                collection and find something you love.</p><Link className="btn btn-dark" to="/shop">Explore
                products <ArrowRight size={17}/></Link></div> : <div className="cart-layout">
                <div className="cart-list">{cart.map(item => {
                    const p = catalog.find(x => x.id === item.id);
                    if (!p) return null;
                    return <div className="cart-item" key={item.id}><Link to={`/product/${p.id}`}><img src={p.image}
                                                                                                       alt={p.name}/></Link>
                        <div className="cart-item-info"><span className="eyebrow">{p.category}</span><Link
                            to={`/product/${p.id}`}
                            className="cart-item-name">{p.name}</Link><strong>{money(p.price)}</strong>
                            <div className="cart-item-actions">
                                <div className="qty qty-small">
                                    <button aria-label="Decrease" onClick={() => update(p.id, item.quantity - 1)}><Minus
                                        size={14}/></button>
                                    <span>{item.quantity}</span>
                                    <button aria-label="Increase" onClick={() => update(p.id, item.quantity + 1)}><Plus
                                        size={14}/></button>
                                </div>
                                <button className="remove-btn" onClick={() => remove(p.id)}><Trash2 size={15}/> Remove
                                </button>
                            </div>
                        </div>
                        <strong className="cart-line-total">{money(p.price * item.quantity)}</strong></div>
                })}</div>
                <aside className="summary-card"><h2>Order summary</h2>
                    <div className="summary-line"><span>Subtotal</span><strong>{money(subtotal)}</strong></div>
                    <div className="summary-line"><span>Shipping</span><span>Calculated later</span></div>
                    <div className="summary-line summary-total"><span>Total</span><strong>{money(subtotal)}</strong>
                    </div>
                    <Link className="btn btn-dark btn-full" to="/checkout">Continue to checkout <ArrowRight size={17}/></Link><Link
                        className="continue-shopping" to="/shop">Continue shopping</Link></aside>
            </div>}</main>
}

