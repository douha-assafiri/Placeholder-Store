import {useState} from 'react'
import {Link,NavLink,useNavigate} from 'react-router-dom'
import {ArrowRight,Menu,Search,ShoppingBag,UserRound,X} from 'lucide-react'
import {useStore} from '../context/StoreContext'
export default function Header(){const [open,setOpen]=useState(false);const [query,setQuery]=useState('');const {count}=useStore();const navigate=useNavigate();const links=[['/','Home'],['/shop','Shop'],['/admin','Admin']];return <>
 <div className="announcement">Thoughtful finds. Everyday favourites. <Link to="/shop">Explore the collection <ArrowRight size={13}/></Link></div>
 <header className="site-header"><div className="header-inner"><Link to="/" className="brand">placeholder<span>.</span><small>STORE</small></Link>
 <nav className="desktop-nav">{links.map(([path,label])=><NavLink key={path} to={path} end={path==='/'} className={({isActive})=>isActive?'active':''}>{label}</NavLink>)}</nav>
 <form className="header-search" onSubmit={e=>{e.preventDefault();navigate('/shop?q='+encodeURIComponent(query));setOpen(false)}}><Search size={18}/><input aria-label="Search products" placeholder="Search for something special..." value={query} onChange={e=>setQuery(e.target.value)}/><button aria-label="Submit search" type="submit"><ArrowRight size={18}/></button></form>
 <div className="header-actions"><Link to="/account" aria-label="Account"><UserRound size={21}/></Link><Link to="/cart" aria-label="Shopping cart" className="cart-icon"><ShoppingBag size={21}/>{count>0&&<span>{count}</span>}</Link><button className="mobile-menu" aria-label="Toggle menu" onClick={()=>setOpen(!open)}>{open?<X/>:<Menu/>}</button></div></div>
 {open&&<nav className="mobile-nav">{links.map(([path,label])=><Link onClick={()=>setOpen(false)} to={path} key={path}>{label}</Link>)}<Link onClick={()=>setOpen(false)} to="/account">My account</Link><Link onClick={()=>setOpen(false)} to="/cart">Cart ({count})</Link></nav>}</header></>}
