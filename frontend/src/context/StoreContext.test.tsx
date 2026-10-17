import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { StoreProvider } from './StoreContext'
import { useStore } from './useStore'
import type { ApiPlace } from '../lib/api'

const lamp: ApiPlace = {
    id: 1, name: 'Lamp', description: 'd', image_path: 'lamp.jpg', stock: true,
    price: 10, category: 'Home', rating: 4, old_price: null, tag: null, quantity: 2,
}
const vase: ApiPlace = { ...lamp, id: 2, name: 'Vase', price: 25, quantity: 5 }

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status })

function mockApi() {
    const fetchMock = vi.fn(async (url: string, options?: RequestInit) => {
        const path = url.replace('/api', '')
        if (path === '/places') return json([lamp, vase])
        if (path === '/accounts/me') return json({ id: 7, name: 'Jo', email: 'jo@test.com', dob: '2000-01-01', role: 'Customer' })
        if (path === '/accounts/me/orders') return json([])
        if (path === '/orders' && options?.method === 'POST') {
            return json({
                id: 3, price: 45, status: 'Processing', created_at: '2026-10-15T10:00:00',
                items: [{ place_id: 1, name: 'Lamp', quantity: 2, price: 10 }, { place_id: 2, name: 'Vase', quantity: 1, price: 25 }],
                first_name: 'Jo', last_name: null, email: null, street: null, city: null, state: null, postcode: null, country: null,
            }, 201)
        }
        return json({ detail: 'Not found' }, 404)
    })
    vi.stubGlobal('fetch', fetchMock)
    return fetchMock
}

async function renderStore() {
    const { result } = renderHook(() => useStore(), { wrapper: StoreProvider })
    await waitFor(() => expect(result.current.catalog).toHaveLength(2))
    return result
}

beforeEach(() => {
    localStorage.clear()
})

afterEach(() => {
    vi.unstubAllGlobals()
})

describe('cart', () => {
    it('loads products from the API', async () => {
        mockApi()
        const store = await renderStore()
        expect(store.current.catalog.map(p => p.name)).toEqual(['Lamp', 'Vase'])
    })

    it('adds items and totals them', async () => {
        mockApi()
        const store = await renderStore()
        act(() => store.current.add(1))
        act(() => store.current.add(2, 2))
        expect(store.current.count).toBe(3)
        expect(store.current.subtotal).toBe(10 + 25 * 2)
    })

    it('never adds more than is in stock', async () => {
        mockApi()
        const store = await renderStore()
        act(() => store.current.add(1, 5))
        act(() => store.current.add(1))
        expect(store.current.cart).toEqual([{ id: 1, quantity: 2 }])
    })

    it('removes an item when its quantity is set to 0', async () => {
        mockApi()
        const store = await renderStore()
        act(() => store.current.add(2))
        act(() => store.current.update(2, 0))
        expect(store.current.cart).toEqual([])
    })

    it('keeps the cart in the browser', async () => {
        mockApi()
        const store = await renderStore()
        act(() => store.current.add(2))
        expect(JSON.parse(localStorage.getItem('ps_cart') ?? '[]')).toEqual([{ id: 2, quantity: 1 }])
    })
})

describe('checkout', () => {
    it('sends the cart as order items and empties it', async () => {
        localStorage.setItem('ps_token', 'abc')
        const fetchMock = mockApi()
        const store = await renderStore()
        await waitFor(() => expect(store.current.user?.name).toBe('Jo'))
        act(() => store.current.add(1, 2))
        act(() => store.current.add(2))

        let order
        await act(async () => {
            order = await store.current.placeOrder({
                first_name: 'Jo', last_name: 'Smith', email: 'jo@test.com', street: '1 Main St',
                city: 'Melbourne', state: 'VIC', postcode: '3000', country: 'Australia',
            })
        })

        const post = fetchMock.mock.calls.find(([url, options]) => url.endsWith('/orders') && options?.method === 'POST')
        expect(JSON.parse(String(post?.[1]?.body)).items).toEqual([{ place_id: 1, quantity: 2 }, { place_id: 2, quantity: 1 }])
        expect(order).toMatchObject({ id: '3', total: 45, status: 'Processing' })
        expect(store.current.cart).toEqual([])
    })
})
