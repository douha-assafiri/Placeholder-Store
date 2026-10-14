
import { useEffect, useState, type ReactNode } from 'react'
import { products, type Product } from '../data/products'
import { Context, type CartItem, type Order, type Store } from './store-context'

function load<T>(key: string, fallback: T): T {
    try {
        const value = localStorage.getItem(key)
        return value ? (JSON.parse(value) as T) : fallback
    } catch {
        return fallback
    }
}

export function StoreProvider({ children }: { children: ReactNode }) {
    const [cart, setCart] = useState<CartItem[]>(() =>
        load('ps_cart', [])
    )

    const [orders, setOrders] = useState<Order[]>(() =>
        load('ps_orders', [])
    )

    const [catalog, setCatalog] = useState<Product[]>(() =>
        load('ps_products', products)
    )

    // Save data to browser storage
    useEffect(() => {
        localStorage.setItem('ps_cart', JSON.stringify(cart))
    }, [cart])

    useEffect(() => {
        localStorage.setItem('ps_orders', JSON.stringify(orders))
    }, [orders])

    useEffect(() => {
        localStorage.setItem('ps_products', JSON.stringify(catalog))
    }, [catalog])

    // Shopping cart functions
    const add = (id: number, quantity = 1) => {
        setCart(prev => {
            const product = catalog.find(p => p.id === id)

            if (!product || product.stock <= 0) {
                return prev
            }

            const existing = prev.find(item => item.id === id)

            if (existing) {
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
    }

    const remove = (id: number) => {
        setCart(prev => prev.filter(item => item.id !== id))
    }

    const update = (id: number, quantity: number) => {
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
    }

    const clear = () => {
        setCart([])
    }

    // Cart totals
    const count = cart.reduce(
        (total, item) => total + item.quantity,
        0
    )

    const subtotal = cart.reduce((total, item) => {
        const product = catalog.find(p => p.id === item.id)

        return total + (product?.price ?? 0) * item.quantity
    }, 0)

    // Checkout
    const placeOrder = (): Order | null => {
        if (cart.length === 0) return null

        const order: Order = {
            id: `PS-${Date.now().toString().slice(-7)}`,
            date: new Date().toLocaleDateString('en-AU'),
            total: subtotal,
            items: [...cart],
            status: 'Processing',
        }

        setOrders(prev => [order, ...prev])
        clear()

        return order
    }

    // Admin product management
    const addProduct = (product: Product) => {
        setCatalog(prev => [product, ...prev])
    }

    const removeProduct = (id: number) => {
        setCatalog(prev => prev.filter(p => p.id !== id))
    }

    const updateOrder = (id: string, status: string) => {
        setOrders(prev =>
            prev.map(order =>
                order.id === id
                    ? { ...order, status }
                    : order
            )
        )
    }

    // Context value
    const value: Store = {
        cart,
        orders,
        catalog,
        add,
        remove,
        update,
        clear,
        placeOrder,
        addProduct,
        removeProduct,
        updateOrder,
        count,
        subtotal,
    }

    return (
        <Context.Provider value={value}>
            {children}
        </Context.Provider>
    )
}
