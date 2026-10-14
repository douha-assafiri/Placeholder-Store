import {Link} from 'react-router-dom'
import {ArrowUpRight,ShoppingBag,Star} from 'lucide-react'
import {type Product,money} from '../data/products'
import { useStore } from '../context/useStore'
export default function ProductCard({product}:{product:Product}){const {add}=useStore();return <article className="product-card"><Link to={`/product/${product.id}`} className="product-photo"><img src={product.image} alt={product.name} loading="lazy"/>{product.tag&&<span className="product-tag">{product.tag}</span>}<span className="product-open"><ArrowUpRight size={18}/></span></Link><div className="product-info"><div className="product-meta"><span>{product.category}</span><span className="rating"><Star size={13} fill="currentColor"/> {product.rating}</span></div><Link to={`/product/${product.id}`} className="product-name">{product.name}</Link><div className="product-bottom"><div><strong>{money(product.price)}</strong>{product.oldPrice&&<del>{money(product.oldPrice)}</del>}</div><button className="add-icon" aria-label={`Add ${product.name} to cart`} onClick={()=>add(product.id)}><ShoppingBag size={18}/></button></div></div></article>}

