import React from 'react';
import Link from 'next/link';
import Head from 'next/head';
import Layout from '../components/Layout';

export default function Home() {
  return (
    <Layout>
      <Head>
        <title>EduAI - Educational Content Generator</title>
        <meta name="description" content="AI-powered educational content generator for teachers and students" />
      </Head>
      
      <div className="container">
        {/* Hero Section */}
        <div className="text-center py-12">
          <h1 className="text-5xl font-bold mb-4" style={{ color: '#5e35b1' }}>
            <span className="text-gray-800">Edu</span>AI
          </h1>
          <h2 className="text-2xl mb-6 text-gray-700">AI-Powered Educational Content Generator</h2>
          <p className="text-xl mb-10 mx-auto max-w-3xl text-gray-600">
            Generate high-quality educational content, deep research, and visualizations for any topic 
            with the power of artificial intelligence.
          </p>
          
          <div className="flex justify-center gap-4">
            <Link href="/content" className="btn">
              Get Started
            </Link>
            <Link href="/deep-research" className="btn-outline">
              Try Research Mode
            </Link>
          </div>
        </div>
        
        {/* Features Section */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          <div className="card">
            <div className="flex items-center mb-4">
              <div className="rounded-full p-3 bg-primary-50 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#5e35b1" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold" style={{ color: '#5e35b1' }}>Content Generator</h3>
            </div>
            <p className="mb-6 text-gray-600">
              Create educational content tailored to any audience level, from elementary to graduate. 
              Perfect for teachers, students, and educational content creators.
            </p>
            <Link href="/content" className="btn">
              Get Started
            </Link>
          </div>
          
          <div className="card">
            <div className="flex items-center mb-4">
              <div className="rounded-full p-3 bg-primary-50 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#5e35b1" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold" style={{ color: '#5e35b1' }}>Deep Research</h3>
            </div>
            <p className="mb-6 text-gray-600">
              Generate comprehensive research content with academic references, key concepts, and 
              visualization prompts for in-depth educational materials.
            </p>
            <Link href="/deep-research" className="btn">
              Explore
            </Link>
          </div>
        </div>
        
        {/* How It Works Section */}
        <div className="card my-12 max-w-4xl mx-auto">
          <h3 className="text-2xl font-bold mb-8 text-center">How It Works</h3>
          <ol className="space-y-6 max-w-2xl mx-auto">
            <li className="flex items-start">
              <div className="flex-shrink-0 flex items-center justify-center rounded-full bg-primary-600 text-white w-10 h-10 mr-4">
                1
              </div>
              <div>
                <h4 className="font-semibold text-lg mb-1">Enter your topic</h4>
                <p className="text-gray-600">Choose an educational topic and select your target audience level</p>
              </div>
            </li>
            <li className="flex items-start">
              <div className="flex-shrink-0 flex items-center justify-center rounded-full bg-primary-600 text-white w-10 h-10 mr-4">
                2
              </div>
              <div>
                <h4 className="font-semibold text-lg mb-1">AI generates content</h4>
                <p className="text-gray-600">Our advanced AI generates high-quality educational materials tailored to your needs</p>
              </div>
            </li>
            <li className="flex items-start">
              <div className="flex-shrink-0 flex items-center justify-center rounded-full bg-primary-600 text-white w-10 h-10 mr-4">
                3
              </div>
              <div>
                <h4 className="font-semibold text-lg mb-1">Use the content</h4>
                <p className="text-gray-600">Use the generated content in your lesson plans, presentations, or research papers</p>
              </div>
            </li>
          </ol>
        </div>
      </div>
    </Layout>
  );
}