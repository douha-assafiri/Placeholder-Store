import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError, toPlace, toProduct, type ApiPlace } from './api'

const place: ApiPlace = {
    id: 1, name: 'Lamp', description: 'A lamp', image_path: 'lamp.jpg', stock: true,
    price: 10, category: 'Home', rating: 4.5, old_price: 15, tag: 'Sale', quantity: 3,
}

const respond = (body: unknown, status = 200) =>
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
        new Response(typeof body === 'string' ? body : JSON.stringify(body), { status }),
    ))

afterEach(() => {
    vi.unstubAllGlobals()
})

describe('toProduct', () => {
    it('maps API fields to frontend fields', () => {
        expect(toProduct(place)).toEqual({
            id: 1, name: 'Lamp', category: 'Home', price: 10, oldPrice: 15, rating: 4.5,
            image: 'lamp.jpg', tag: 'Sale', description: 'A lamp', stock: 3,
        })
    })

    it('treats an untracked quantity as plenty in stock', () => {
        expect(toProduct({ ...place, quantity: null }).stock).toBe(99)
    })

    it('treats an untracked, out of stock place as 0', () => {
        expect(toProduct({ ...place, quantity: null, stock: false }).stock).toBe(0)
    })

    it('leaves out an empty sale price and tag', () => {
        const product = toProduct({ ...place, old_price: null, tag: null })
        expect(product.oldPrice).toBeUndefined()
        expect(product.tag).toBeUndefined()
    })
})

describe('toPlace', () => {
    it('maps frontend fields back to API fields', () => {
        const { id, ...product } = toProduct(place)
        expect(id).toBe(1)
        expect(toPlace(product)).toEqual({
            name: 'Lamp', category: 'Home', price: 10, old_price: 15, rating: 4.5,
            image_path: 'lamp.jpg', tag: 'Sale', description: 'A lamp', quantity: 3,
        })
    })
})

describe('api', () => {
    it('returns the JSON response', async () => {
        respond([place])
        await expect(api('/places')).resolves.toEqual([place])
    })

    it('returns plain text responses as text', async () => {
        respond('Account created', 201)
        await expect(api('/accounts/create', { method: 'POST', body: {} })).resolves.toBe('Account created')
    })

    it('sends the token and a JSON body', async () => {
        respond({})
        await api('/orders', { method: 'POST', token: 'abc', body: { items: [] } })
        const [url, options] = vi.mocked(fetch).mock.calls[0]
        expect(url).toBe('http://127.0.0.1:8000/api/orders')
        expect(options).toMatchObject({
            method: 'POST',
            headers: { Authorization: 'Bearer abc', 'Content-Type': 'application/json' },
            body: '{"items":[]}',
        })
    })

    it('throws the API error message', async () => {
        respond({ detail: 'Incorrect email or password' }, 400)
        await expect(api('/accounts/login')).rejects.toEqual(new ApiError(400, 'Incorrect email or password'))
    })

    it('uses the first field error for invalid input', async () => {
        respond({ detail: [{ msg: 'Field required' }] }, 422)
        await expect(api('/orders')).rejects.toThrow('Field required')
    })

    it('falls back to a default message when the error is not JSON', async () => {
        respond('Bad gateway', 502)
        await expect(api('/places')).rejects.toThrow('Request failed (502)')
    })
})
