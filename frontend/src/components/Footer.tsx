import {Link} from 'react-router-dom'
import {Camera, Mail, ArrowUpRight} from 'lucide-react'

export default function Footer() {
    return <footer className="footer">
        <div className="container footer-grid">
            <div><Link className="brand footer-brand" to="/">placeholder<span>.</span><small>STORE</small></Link>
                <p>Objects for living well. Carefully selected essentials for the everyday.</p></div>
            <div><h4>Explore</h4><Link to="/shop">Shop all</Link><Link
                to="/shop?category=Electronics">Electronics</Link><Link to="/shop?category=Fashion">Fashion</Link><Link
                to="/shop?category=Accessories">Accessories</Link></div>
            <div><h4>Information</h4><Link to="/account">My account</Link><Link to="/cart">Shopping bag</Link><Link
                to="/admin">Admin demo</Link><span>Melbourne, Australia</span></div>
            <div><h4>Stay in the loop</h4><p>Something good is always around the corner.</p><a
                href="mailto:hello@example.com"><Mail size={16}/> Get in touch <ArrowUpRight size={14}/></a><a
                href="https://instagram.com" target="_blank" rel="noreferrer"><Camera size={16}/> Camera <ArrowUpRight
                size={14}/></a></div>
        </div>
        <div className="container footer-bottom"><span>© 2026 Placeholder Store. Demo storefront.</span><span>Designed for the everyday.</span>
        </div>
    </footer>
}
