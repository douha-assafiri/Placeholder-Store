import { useState, type SubmitEvent } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, Box, ClipboardList, DollarSign, Pencil, Plus, Trash2 } from 'lucide-react'
import { money, type Product } from '../data/products'
import { useStore } from '../context/useStore'
import { formText } from '../lib/form'

const DEFAULT_IMAGE = 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=900'

export default function AdminPage() {
    const { catalog, allOrders, addProduct, updateProduct, removeProduct, updateOrder, isStaff, user } = useStore()
    const [showForm, setShowForm] = useState(false)
    const [editing, setEditing] = useState<Product | null>(null)
    const [message, setMessage] = useState('')
    const categories = [...new Set(['Electronics', 'Fashion', 'Accessories', 'Home & Living', ...catalog.map(p => p.category)])]

    if (!isStaff) {
        return (
            <main className="container page-space empty-state">
                <h1>Staff only</h1>
                <p>{user ? 'Your account does not have access to the admin dashboard.' : 'Sign in with a staff account to manage the store.'}</p>
                <Link className="btn btn-dark" to="/account">{user ? 'Back to my account' : 'Sign in'}</Link>
            </main>
        )
    }

    const run = async (action: () => Promise<void>) => {
        setMessage('')
        try {
            await action()
        } catch (error) {
            setMessage(error instanceof Error ? error.message : 'Something went wrong')
        }
    }
    const openForm = (product: Product | null) => {
        setEditing(product)
        setShowForm(true)
    }
    const submit = (e: SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()
        const form = new FormData(e.currentTarget)
        const oldPrice = formText(form, 'oldPrice')
        const tag = formText(form, 'tag')
        const product: Omit<Product, 'id'> = {
            name: formText(form, 'name'),
            category: formText(form, 'category'),
            price: Number(formText(form, 'price')),
            oldPrice: oldPrice ? Number(oldPrice) : undefined,
            stock: Number(formText(form, 'stock')),
            rating: Number(formText(form, 'rating')),
            image: formText(form, 'image') || DEFAULT_IMAGE,
            tag: tag || undefined,
            description: formText(form, 'description'),
        }
        void run(async () => {
            if (editing) await updateProduct(editing.id, product)
            else await addProduct(product)
            setShowForm(false)
            setEditing(null)
        })
    }

    return (
        <main className="container page-space">
            <div className="section-heading">
                <div>
                    <span className="eyebrow">STORE MANAGEMENT</span>
                    <h1>Admin dashboard<span className="accent-dot">.</span></h1>
                    <p>Manage products and orders for the store.</p>
                </div>
                <button type="button" className="btn btn-dark" onClick={() => (showForm ? setShowForm(false) : openForm(null))}>
                    <Plus size={17} /> Add product
                </button>
            </div>
            {message && <div className="demo-notice">{message}</div>}
            <div className="admin-stats">
                <div><Box /><span>Products</span><strong>{catalog.length}</strong></div>
                <div><ClipboardList /><span>Orders</span><strong>{allOrders.length}</strong></div>
                <div><DollarSign /><span>Revenue</span><strong>{money(allOrders.reduce((s, o) => s + o.total, 0))}</strong></div>
            </div>
            {showForm && (
                <form className="admin-form" onSubmit={submit} key={editing?.id ?? 'new'}>
                    <h2>{editing ? `Edit ${editing.name}` : 'Add a product'}</h2>
                    <div className="field-grid">
                        <label>Product name<input name="name" required defaultValue={editing?.name} /></label>
                        <label>Category<select name="category" defaultValue={editing?.category}>
                                {categories.map(c => <option key={c}>{c}</option>)}
                            </select>
                        </label>
                        <label>Price (AUD)<input name="price" required type="number" min="0.01" step="0.01" defaultValue={editing?.price} /></label>
                        <label>Old price (AUD, for sales)<input name="oldPrice" type="number" min="0.01" step="0.01" defaultValue={editing?.oldPrice} /></label>
                        <label>Stock<input name="stock" required type="number" min="0" defaultValue={editing?.stock} /></label>
                        <label>Rating (0-5)<input name="rating" required type="number" min="0" max="5" step="0.1" defaultValue={editing?.rating ?? 5} /></label>
                        <label>Tag<input name="tag" placeholder="New, Sale, Bestseller..." defaultValue={editing?.tag} /></label>
                    </div>
                    <label>Image URL<input name="image" type="url" placeholder="https://..." defaultValue={editing?.image} /></label>
                    <label>Description<textarea name="description" required rows={3} defaultValue={editing?.description} /></label>
                    <button type="submit" className="btn btn-dark">Save product</button>
                </form>
            )}
            <div className="admin-panel">
                <div className="admin-panel-title"><h2>Products</h2><span>{catalog.length} items</span></div>
                <div className="table-scroll">
                    <table>
                        <thead><tr><th>Product</th><th>Category</th><th>Price</th><th>Stock</th><th>Action</th></tr></thead>
                        <tbody>
                            {catalog.map(p => (
                                <tr key={p.id}>
                                    <td>
                                        <div className="admin-product">
                                            <img src={p.image} alt="" />
                                            <Link to={`/product/${p.id}`}>{p.name} <ArrowUpRight size={13} /></Link>
                                        </div>
                                    </td>
                                    <td>{p.category}</td>
                                    <td>{money(p.price)}</td>
                                    <td>{p.stock}</td>
                                    <td>
                                        <button type="button" className="remove-btn" onClick={() => openForm(p)}><Pencil size={15} /> Edit</button>
                                        <button type="button" className="remove-btn" onClick={() => {
                                            if (window.confirm(`Remove ${p.name}?`)) void run(() => removeProduct(p.id))
                                        }}><Trash2 size={15} /> Delete</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
            <div className="admin-panel">
                <div className="admin-panel-title"><h2>Orders</h2><span>{allOrders.length} orders</span></div>
                {allOrders.length === 0 ? (
                    <p className="admin-empty">No orders yet. Orders placed through checkout show up here.</p>
                ) : (
                    <div className="table-scroll">
                        <table>
                            <thead><tr><th>Order ID</th><th>Date</th><th>Customer</th><th>Items</th><th>Total</th><th>Status</th></tr></thead>
                            <tbody>
                                {allOrders.map(o => (
                                    <tr key={o.id}>
                                        <td>{o.id}</td>
                                        <td>{o.date}</td>
                                        <td>{[o.details.first_name, o.details.last_name].filter(Boolean).join(' ') || '-'}</td>
                                        <td>{o.items.reduce((s, i) => s + i.quantity, 0)}</td>
                                        <td>{money(o.total)}</td>
                                        <td>
                                            <select aria-label={`Status for ${o.id}`} value={o.status}
                                                    onChange={e => void run(() => updateOrder(o.id, e.target.value))}>
                                                <option>Processing</option>
                                                <option>Shipped</option>
                                                <option>Delivered</option>
                                                <option>Cancelled</option>
                                            </select>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </main>
    )
}
