import { describe, expect, it } from 'vitest'
import { formText } from './form'

describe('formText', () => {
    it('returns text values', () => {
        const form = new FormData()
        form.append('name', 'Jo')
        expect(formText(form, 'name')).toBe('Jo')
    })

    it('returns an empty string for missing fields and files', () => {
        const form = new FormData()
        form.append('photo', new File(['x'], 'photo.png'))
        expect(formText(form, 'missing')).toBe('')
        expect(formText(form, 'photo')).toBe('')
    })
})
