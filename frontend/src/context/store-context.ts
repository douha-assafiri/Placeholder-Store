
import { createContext } from 'react'
import type { Product } from '../data/products'
import type { Account } from '../lib/api'

export type CartItem = {
    id: number
    quantity: number
}

export type OrderItem = CartItem & {
    name: string
    price: number
}

export type OrderDetails = {
    first_name: string
    last_name: string
    email: string
    street: string
    city: string
    state: string
    postcode: string
    country: string
}

export type Order = {
    id: string
    date: string
    total: number
    items: OrderItem[]
    status: string
    details: Partial<OrderDetails>
}

export type Store = {
    cart: CartItem[]
    orders: Order[]
    allOrders: Order[]
    catalog: Product[]
    loading: boolean

    add: (id: number, quantity?: number) => void
    remove: (id: number) => void
    update: (id: number, quantity: number) => void
    clear: () => void

    placeOrder: (details: OrderDetails) => Promise<Order | null>

    addProduct: (product: Omit<Product, 'id'>) => Promise<void>
    updateProduct: (id: number, product: Omit<Product, 'id'>) => Promise<void>
    removeProduct: (id: number) => Promise<void>
    updateOrder: (id: string, status: string) => Promise<void>

    user: Account | null
    isStaff: boolean
    login: (email: string, password: string) => Promise<void>
    register: (account: { name: string; email: string; password: string; dob: string }) => Promise<void>
    logout: () => Promise<void>
    updateProfile: (account: { name: string; email: string; dob: string }) => Promise<void>
    changePassword: (oldPassword: string, newPassword: string) => Promise<void>
    deleteAccount: () => Promise<void>

    count: number
    subtotal: number
}

export const Context = createContext<Store | null>(null)
