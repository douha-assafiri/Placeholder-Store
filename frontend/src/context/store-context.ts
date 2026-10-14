
import { createContext } from 'react'
import type { Product } from '../data/products'

export type CartItem = {
    id: number
    quantity: number
}

export type Order = {
    id: string
    date: string
    total: number
    items: CartItem[]
    status: string
}

export type Store = {
    cart: CartItem[]
    orders: Order[]
    catalog: Product[]

    add: (id: number, quantity?: number) => void
    remove: (id: number) => void
    update: (id: number, quantity: number) => void
    clear: () => void

    placeOrder: () => Order | null

    addProduct: (product: Product) => void
    removeProduct: (id: number) => void
    updateOrder: (id: string, status: string) => void

    count: number
    subtotal: number
}

export const Context = createContext<Store | null>(null)
