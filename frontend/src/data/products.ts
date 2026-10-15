export type Product = {
    id: number;
    name: string;
    category: string;
    price: number;
    oldPrice?: number;
    rating: number;
    image: string;
    tag?: string;
    description: string;
    stock: number
}
export const money = (amount: number) => new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD'
}).format(amount)
