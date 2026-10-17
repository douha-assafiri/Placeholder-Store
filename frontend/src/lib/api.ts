import type { Product } from '../data/products'

// Override only if api is on another origin.
const BASE_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

export class ApiError extends Error {
    status: number

    constructor(status: number, message: string) {
        super(message)
        this.status = status
    }
}

export async function api<T>(path: string, options: { method?: string; body?: unknown; token?: string | null } = {}): Promise<T> {
    const headers: Record<string, string> = {}
    if (options.body !== undefined) headers['Content-Type'] = 'application/json'
    if (options.token) headers.Authorization = `Bearer ${options.token}`

    const response = await fetch(BASE_URL + path, {
        method: options.method ?? 'GET',
        headers,
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
    })

    if (!response.ok) {
        let message = `Request failed (${response.status})`
        const data = await response.json().catch(() => null)
        // detail is a string or a list of field errors
        if (typeof data?.detail === 'string') message = data.detail
        else if (Array.isArray(data?.detail) && data.detail[0]?.msg) message = data.detail[0].msg
        throw new ApiError(response.status, message)
    }

    const text = await response.text()
    try {
        return (text ? JSON.parse(text) : undefined) as T
    } catch {
        return text as T
    }
}

export type ApiPlace = {
    id: number
    name: string
    description: string
    image_path: string
    stock: boolean
    price: number
    category: string
    rating: number
    old_price: number | null
    tag: string | null
    quantity: number | null
}

export type ApiOrder = {
    id: number
    price: number
    status: string
    created_at: string
    items: { place_id: number | null; name: string; quantity: number; price: number }[]
    first_name: string | null
    last_name: string | null
    email: string | null
    street: string | null
    city: string | null
    state: string | null
    postcode: string | null
    country: string | null
}

export type Account = {
    id: number
    name: string
    email: string
    dob: string
    role: 'Customer' | 'Staff'
}

export function toProduct(place: ApiPlace): Product {
    return {
        id: place.id,
        name: place.name,
        category: place.category,
        price: place.price,
        oldPrice: place.old_price ?? undefined,
        rating: place.rating,
        image: place.image_path,
        tag: place.tag ?? undefined,
        description: place.description,
        // Untracked quantity counts as plenty in stock
        stock: place.quantity ?? (place.stock ? 99 : 0),
    }
}

export function toPlace(product: Omit<Product, 'id'>) {
    return {
        name: product.name,
        category: product.category,
        price: product.price,
        old_price: product.oldPrice ?? null,
        rating: product.rating,
        image_path: product.image,
        tag: product.tag ?? null,
        description: product.description,
        quantity: product.stock,
    }
}
