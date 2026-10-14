import {createContext,useContext,useEffect,useMemo,useState,type ReactNode} from 'react'
import {products,type Product} from '../data/products'
type CartItem={id:number;quantity:number}
type Order={id:string;date:string;total:number;items:CartItem[];status:string}
type Store={cart:CartItem[];orders:Order[];catalog:Product[];add:(id:number,quantity?:number)=>void;remove:(id:number)=>void;update:(id:number,quantity:number)=>void;clear:()=>void;placeOrder:()=>Order|null;addProduct:(product:Product)=>void;removeProduct:(id:number)=>void;updateOrder:(id:string,status:string)=>void;count:number;subtotal:number}
const Context=createContext<Store|null>(null)
function load<T>(key:string,fallback:T):T{try{const v=localStorage.getItem(key);return v?JSON.parse(v) as T:fallback}catch{return fallback}}
export function StoreProvider({children}:{children:ReactNode}){
 const [cart,setCart]=useState<CartItem[]>(()=>load('ps_cart',[]))
 const [orders,setOrders]=useState<Order[]>(()=>load('ps_orders',[]))
 const [catalog,setCatalog]=useState<Product[]>(()=>load('ps_products',products))
 useEffect(()=>localStorage.setItem('ps_cart',JSON.stringify(cart)),[cart])
 useEffect(()=>localStorage.setItem('ps_orders',JSON.stringify(orders)),[orders])
 useEffect(()=>localStorage.setItem('ps_products',JSON.stringify(catalog)),[catalog])
 const add=(id:number,quantity=1)=>setCart(prev=>{const p=catalog.find(x=>x.id===id);if(!p)return prev;const existing=prev.find(x=>x.id===id);return existing?prev.map(x=>x.id===id?{...x,quantity:Math.min(p.stock,x.quantity+quantity)}:x):[...prev,{id,quantity:Math.min(p.stock,Math.max(1,quantity))}]})
 const remove=(id:number)=>setCart(prev=>prev.filter(x=>x.id!==id))
 const update=(id:number,quantity:number)=>setCart(prev=>quantity<=0?prev.filter(x=>x.id!==id):prev.map(x=>x.id===id?{...x,quantity:Math.min(catalog.find(p=>p.id===id)?.stock??quantity,quantity)}:x))
 const clear=()=>setCart([])
 const count=cart.reduce((s,x)=>s+x.quantity,0)
 const subtotal=cart.reduce((s,x)=>s+(catalog.find(p=>p.id===x.id)?.price??0)*x.quantity,0)
 const placeOrder=()=>{if(!cart.length)return null;const order={id:`PS-${Date.now().toString().slice(-7)}`,date:new Date().toLocaleDateString('en-AU'),total:subtotal,items:[...cart],status:'Processing'};setOrders(prev=>[order,...prev]);clear();return order}
 const value=useMemo(()=>({cart,orders,catalog,add,remove,update,clear,placeOrder,addProduct:(p:Product)=>setCatalog(prev=>[p,...prev]),removeProduct:(id:number)=>setCatalog(prev=>prev.filter(p=>p.id!==id)),updateOrder:(id:string,status:string)=>setOrders(prev=>prev.map(o=>o.id===id?{...o,status}:o)),count,subtotal}),[cart,orders,catalog,count,subtotal])
 return <Context.Provider value={value}>{children}</Context.Provider>
}
export function useStore(){const store=useContext(Context);if(!store)throw new Error('StoreProvider missing');return store}
