import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

/**
 * Modern navigation bar component
 * 
 * @returns {JSX.Element} Navbar component
 */
const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const router = useRouter();
  
  const isActive = (path) => router.pathname === path;
  
  return (
    <nav className="nav">
      <div className="container nav-container">
        <Link href="/" className="nav-logo">
          <span className="text-2xl font-bold">Edu</span>
          <span className="text-2xl font-bold" style={{ color: '#5e35b1' }}>AI</span>
        </Link>
        
        <div className="nav-links hidden md:flex">
          <Link href="/" className={`nav-link ${isActive('/') ? 'nav-link-active' : ''}`}>
            Home
          </Link>
          <Link href="/content" className={`nav-link ${isActive('/content') ? 'nav-link-active' : ''}`}>
            Content
          </Link>
          <Link href="/streaming-content" className={`nav-link ${isActive('/streaming-content') ? 'nav-link-active' : ''}`}>
            Streaming
          </Link>
          <Link href="/deep-research" className={`nav-link ${isActive('/deep-research') ? 'nav-link-active' : ''}`}>
            Research
          </Link>
        </div>
        
        <button 
          className="md:hidden flex items-center justify-center p-2 rounded-md bg-gray-100 hover:bg-gray-200 transition-colors"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>
      </div>
      
      {mobileMenuOpen && (
        <div className="md:hidden container py-4 bg-white border-t border-gray-200 animate-fadeIn">
          <Link href="/" className={`block py-2 px-3 rounded-md ${isActive('/') ? 'nav-link-active' : 'nav-link'}`}>
            Home
          </Link>
          <Link href="/content" className={`block py-2 px-3 rounded-md ${isActive('/content') ? 'nav-link-active' : 'nav-link'}`}>
            Content
          </Link>
          <Link href="/streaming-content" className={`block py-2 px-3 rounded-md ${isActive('/streaming-content') ? 'nav-link-active' : 'nav-link'}`}>
            Streaming
          </Link>
          <Link href="/deep-research" className={`block py-2 px-3 rounded-md ${isActive('/deep-research') ? 'nav-link-active' : 'nav-link'}`}>
            Research
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
