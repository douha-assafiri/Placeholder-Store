
import { useContext } from 'react'
import { Context } from './store-context'

export function useStore() {
    const store = useContext(Context)

    if (!store) {
        throw new Error('StoreProvider missing')
    }

    return store
}
