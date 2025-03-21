import React from 'react';
import Navbar from './Navbar';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      <main className="flex-grow py-6">
        {children}
      </main>
      <footer className="py-6 bg-white border-t border-gray-200">
        <div className="container text-center text-gray-600">
          <p className="text-sm">&copy; {new Date().getFullYear()} EduAI - Educational Content Generator. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;