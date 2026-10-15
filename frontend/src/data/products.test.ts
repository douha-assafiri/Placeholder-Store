import { describe, expect, it } from 'vitest'
import { money } from './products'

describe('money', () => {
    it('formats prices in Australian dollars', () => {
        expect(money(149)).toBe('$149.00')
        expect(money(9.5)).toBe('$9.50')
    })
})
