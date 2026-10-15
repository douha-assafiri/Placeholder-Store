// Values can be files, these forms only use text
export const formText = (form: FormData, name: string): string => {
    const value = form.get(name)
    return typeof value === 'string' ? value : ''
}
