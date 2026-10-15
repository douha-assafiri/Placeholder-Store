import {useMemo, useState} from 'react'
import {useSearchParams} from 'react-router-dom'
import {Search, SlidersHorizontal, X} from 'lucide-react'
import ProductCard from '../components/ProductCard'
import {useStore} from '../context/useStore'

export default function BrowsePage() {
    const {catalog} = useStore();
    const [params, setParams] = useSearchParams();
    const [search, setSearch] = useState(params.get('q') ?? '');
    const [sort, setSort] = useState('featured');
    const category = params.get('category') ?? 'All';
    const minPrice = params.get('min') ?? '';
    const maxPrice = params.get('max') ?? '';
    const inStock = params.get('stock') === '1';
    const categories = ['All', ...new Set(catalog.map(p => p.category))];
    const visible = useMemo(() => {
        const q = (params.get('q') ?? '').toLowerCase();
        const data = catalog.filter(p => (category === 'All' || p.category === category) && (!minPrice || p.price >= Number(minPrice)) && (!maxPrice || p.price <= Number(maxPrice)) && (!inStock || p.stock > 0) && (`${p.name} ${p.category} ${p.description}`).toLowerCase().includes(q));
        if (sort === 'low') data.sort((a, b) => a.price - b.price);
        if (sort === 'high') data.sort((a, b) => b.price - a.price);
        if (sort === 'rating') data.sort((a, b) => b.rating - a.rating);
        return data
    }, [catalog, category, minPrice, maxPrice, inStock, params, sort]);
    const change = (key: string, value: string) => {
        const next = new URLSearchParams(params);
        if (!value || value === 'All') next.delete(key); else next.set(key, value);
        setParams(next)
    };
    return <main className="container page-space">
        <div className="page-intro"><span className="eyebrow">CURATED WITH CARE</span><h1>Shop the collection<span
            className="accent-dot">.</span></h1><p>Thoughtfully chosen pieces for whatever your day has in store.</p>
        </div>
        <div className="shop-layout">
            <aside className="shop-sidebar">
                <div className="sidebar-title"><SlidersHorizontal size={18}/> Refine your search</div>
                <h3>Categories</h3>
                <div className="filter-options">{categories.map(c => <button key={c}
                                                                             onClick={() => change('category', c)}
                                                                             className={category === c ? 'selected' : ''}>{c}<span>{c === 'All' ? catalog.length : catalog.filter(p => p.category === c).length}</span>
                </button>)}</div>
                <h3>Price (AUD)</h3>
                <div className="filter-options">
                    <label>Min<input type="number" min="0" aria-label="Minimum price" value={minPrice} onChange={e => change('min', e.target.value)}/></label>
                    <label>Max<input type="number" min="0" aria-label="Maximum price" value={maxPrice} onChange={e => change('max', e.target.value)}/></label>
                    <label><input type="checkbox" checked={inStock} onChange={e => change('stock', e.target.checked ? '1' : '')}/> In stock only</label>
                </div>
                <div className="sidebar-note">Good design. Everyday prices. Always something worth discovering.</div>
            </aside>
            <div>
                <div className="shop-toolbar">
                    <form className="shop-search" onSubmit={e => {
                        e.preventDefault();
                        change('q', search)
                    }}><Search size={18}/><input placeholder="Search products..." aria-label="Search products"
                                                 value={search} onChange={e => setSearch(e.target.value)}/>{search &&
                        <button type="button" aria-label="Clear search" onClick={() => {
                            setSearch('');
                            change('q', '')
                        }}><X size={16}/></button>}</form>
                    <span className="results-count">{visible.length} products</span><select aria-label="Sort products"
                                                                                            value={sort}
                                                                                            onChange={e => setSort(e.target.value)}>
                    <option value="featured">Featured</option>
                    <option value="low">Price: Low to high</option>
                    <option value="high">Price: High to low</option>
                    <option value="rating">Top rated</option>
                </select></div>
                <div className="products-grid shop-products">{visible.map(p => <ProductCard key={p.id}
                                                                                            product={p}/>)}</div>
                {visible.length === 0 &&
                    <div className="empty-state"><h2>No products found</h2><p>Try a different search or category.</p>
                        <button className="btn btn-dark" onClick={() => {
                            setSearch('');
                            setParams({})
                        }}>Clear filters
                        </button>
                    </div>}</div>
        </div>
    </main>
}

