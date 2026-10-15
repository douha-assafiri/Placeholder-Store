
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { type Product } from '../data/products'
import { Context, type CartItem, type Order, type OrderDetails, type Store } from './store-context'
import { api, ApiError, toPlace, toProduct, type Account, type ApiOrder, type ApiPlace } from '../lib/api'

function load<T>(key: string, fallback: T): T {
    try {
        const value = localStorage.getItem(key)
        return value ? (JSON.parse(value) as T) : fallback
    } catch {
        return fallback
    }
}

function toOrder(order: ApiOrder): Order {
    return {
        id: String(order.id),
        date: new Date(order.created_at).toLocaleDateString('en-AU'),
        total: order.price,
        items: order.items.map(item => ({
            id: item.place_id ?? 0,
            quantity: item.quantity,
            name: item.name,
            price: item.price,
        })),
        status: order.status,
        details: {
            first_name: order.first_name ?? undefined,
            last_name: order.last_name ?? undefined,
            email: order.email ?? undefined,
            street: order.street ?? undefined,
            city: order.city ?? undefined,
            state: order.state ?? undefined,
            postcode: order.postcode ?? undefined,
            country: order.country ?? undefined,
        },
    }
}

export function StoreProvider({ children }: Readonly<{ children: ReactNode }>) {
    const [cart, setCart] = useState<CartItem[]>(() =>
        load('ps_cart', [])
    )

    const [orders, setOrders] = useState<Order[]>([])
    const [allOrders, setAllOrders] = useState<Order[]>([])
    const [catalog, setCatalog] = useState<Product[]>([])
    const [loading, setLoading] = useState(true)

    const [token, setToken] = useState<string | null>(() =>
        localStorage.getItem('ps_token')
    )
    const [user, setUser] = useState<Account | null>(null)
    const isStaff = user?.role === 'Staff'

    const signOutLocally = useCallback(() => {
        setToken(null)
        setUser(null)
        setOrders([])
        setAllOrders([])
    }, [])

    // Save data to browser storage
    useEffect(() => {
        localStorage.setItem('ps_cart', JSON.stringify(cart))
    }, [cart])

    useEffect(() => {
        if (token) localStorage.setItem('ps_token', token)
        else localStorage.removeItem('ps_token')
    }, [token])

    const refreshCatalog = useCallback(async () => {
        try {
            const places = await api<ApiPlace[]>('/places')
            setCatalog(places.map(toProduct))
        } finally {
            setLoading(false)
        }
    }, [])

    const refreshOrders = useCallback(async () => {
        if (!token) return
        const mine = await api<ApiOrder[]>('/accounts/me/orders', { token })
        setOrders(mine.map(toOrder))
        if (user?.role === 'Staff') {
            const every = await api<ApiOrder[]>('/orders', { token })
            setAllOrders(every.map(toOrder))
        } else {
            setAllOrders([])
        }
    }, [token, user?.role])

    useEffect(() => {
        refreshCatalog().catch(() => undefined)
    }, [refreshCatalog])

    useEffect(() => {
        if (!token) return
        api<Account>('/accounts/me', { token })
            .then(setUser)
            .catch(error => {
                // Token expired or logged out
                if (error instanceof ApiError && error.status === 401) signOutLocally()
            })
    }, [token, signOutLocally])

    useEffect(() => {
        refreshOrders().catch(() => undefined)
    }, [refreshOrders])

    // Shopping cart functions
    const add = useCallback((id: number, quantity = 1) => {
        setCart(prev => {
            const product = catalog.find(p => p.id === id)

            if (!product || product.stock <= 0) {
                return prev
            }

            const inCart = prev.some(item => item.id === id)

            if (inCart) {
                return prev.map(item =>
                    item.id === id
                        ? {
                            ...item,
                            quantity: Math.min(
                                product.stock,
                                item.quantity + quantity
                            ),
                        }
                        : item
                )
            }

            return [
                ...prev,
                {
                    id,
                    quantity: Math.min(
                        product.stock,
                        Math.max(1, quantity)
                    ),
                },
            ]
        })
    }, [catalog])

    const remove = useCallback((id: number) => {
        setCart(prev => prev.filter(item => item.id !== id))
    }, [])

    const update = useCallback((id: number, quantity: number) => {
        setCart(prev => {
            if (quantity <= 0) {
                return prev.filter(item => item.id !== id)
            }

            return prev.map(item => {
                if (item.id !== id) return item

                const product = catalog.find(p => p.id === id)

                return {
                    ...item,
                    quantity: Math.min(
                        product?.stock ?? quantity,
                        quantity
                    ),
                }
            })
        })
    }, [catalog])

    const clear = useCallback(() => {
        setCart([])
    }, [])

    // Cart totals
    const count = useMemo(() => cart.reduce(
        (total, item) => total + item.quantity,
        0
    ), [cart])

    const subtotal = useMemo(() => cart.reduce((total, item) => {
        const product = catalog.find(p => p.id === item.id)

        return total + (product?.price ?? 0) * item.quantity
    }, 0), [cart, catalog])

    // Checkout
    const placeOrder = useCallback(async (details: OrderDetails): Promise<Order | null> => {
        if (cart.length === 0) return null

        const created = await api<ApiOrder>('/orders', {
            method: 'POST',
            token,
            body: { items: cart.map(item => ({ place_id: item.id, quantity: item.quantity })), ...details },
        })
        const order = toOrder(created)

        setOrders(prev => [order, ...prev])
        clear()
        await Promise.all([refreshCatalog(), refreshOrders()])

        return order
    }, [cart, token, clear, refreshCatalog, refreshOrders])

    // Admin product management
    const addProduct = useCallback(async (product: Omit<Product, 'id'>) => {
        await api('/places', { method: 'POST', token, body: toPlace(product) })
        await refreshCatalog()
    }, [token, refreshCatalog])

    const updateProduct = useCallback(async (id: number, product: Omit<Product, 'id'>) => {
        await api(`/places/${id}`, { method: 'PATCH', token, body: toPlace(product) })
        await refreshCatalog()
    }, [token, refreshCatalog])

    const removeProduct = useCallback(async (id: number) => {
        await api(`/places/${id}`, { method: 'DELETE', token })
        await refreshCatalog()
    }, [token, refreshCatalog])

    const updateOrder = useCallback(async (id: string, status: string) => {
        await api(`/orders/${id}/status`, { method: 'PATCH', token, body: { status } })
        await refreshOrders()
    }, [token, refreshOrders])

    const login = useCallback(async (email: string, password: string) => {
        const result = await api<{ token: string; id: number }>('/accounts/login', {
            method: 'POST',
            body: { email, password },
        })
        setToken(result.token)
    }, [])

    const register = useCallback(async (account: { name: string; email: string; password: string; dob: string }) => {
        await api('/accounts/create', {
            method: 'POST',
            body: { ...account, dob: `${account.dob}T00:00:00` },
        })
        await login(account.email, account.password)
    }, [login])

    const logout = useCallback(async () => {
        // Still sign out if the token already expired
        await api('/accounts/logout', { method: 'POST', token }).catch(() => undefined)
        signOutLocally()
    }, [token, signOutLocally])

    const updateProfile = useCallback(async (account: { name: string; email: string; dob: string }) => {
        await api('/accounts/me', {
            method: 'PATCH',
            token,
            body: { ...account, dob: `${account.dob}T00:00:00` },
        })
        setUser(await api<Account>('/accounts/me', { token }))
    }, [token])

    const changePassword = useCallback(async (oldPassword: string, newPassword: string) => {
        await api('/accounts/me/password', {
            method: 'PATCH',
            token,
            body: { old_password: oldPassword, new_password: newPassword },
        })
    }, [token])

    const deleteAccount = useCallback(async () => {
        await api('/accounts/me', { method: 'DELETE', token })
        signOutLocally()
    }, [token, signOutLocally])

    // Context value
    // Stable value avoids needless re-renders
    const value: Store = useMemo(() => ({
        cart,
        orders,
        allOrders,
        catalog,
        loading,
        add,
        remove,
        update,
        clear,
        placeOrder,
        addProduct,
        updateProduct,
        removeProduct,
        updateOrder,
        user,
        isStaff,
        login,
        register,
        logout,
        updateProfile,
        changePassword,
        deleteAccount,
        count,
        subtotal,
    }), [
        cart, orders, allOrders, catalog, loading, add, remove, update, clear, placeOrder, addProduct, updateProduct, removeProduct, updateOrder, user, isStaff, login, register, logout, updateProfile, changePassword, deleteAccount, count, subtotal,
    ])

    return (
        <Context.Provider value={value}>
            {children}
        </Context.Provider>
    )
}
