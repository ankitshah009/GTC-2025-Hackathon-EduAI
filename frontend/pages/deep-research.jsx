import React, { useState } from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';

export default function DeepResearch() {
  const [topic, setTopic] = useState('');
  const [details, setDetails] = useState('');
  const [level, setLevel] = useState('undergraduate');
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/generate-research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          details,
          level,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate research');
      }
      
      const data = await response.json();
      setContent(data);
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Head>
        <title>Deep Research | EduAI</title>
        <meta name="description" content="Generate in-depth research content with AI" />
      </Head>
      
      <div className="container py-8">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4" style={{ color: '#5e35b1' }}>Deep Research Generator</h1>
            <p className="text-gray-600">Create comprehensive research content with academic references and key concepts.</p>
          </div>
          
          <div className="card">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="topic" className="form-label">Research Topic</label>
                <input
                  id="topic"
                  type="text"
                  className="form-input"
                  placeholder="e.g. Quantum Computing, Climate Change Impact, Artificial Intelligence Ethics"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="details" className="form-label">Specific Details (optional)</label>
                <textarea
                  id="details"
                  className="form-textarea"
                  placeholder="Any specific aspects of the topic you want to focus on?"
                  value={details}
                  onChange={(e) => setDetails(e.target.value)}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="level" className="form-label">Academic Level</label>
                <select
                  id="level"
                  className="form-select"
                  value={level}
                  onChange={(e) => setLevel(e.target.value)}
                >
                  <option value="high-school">High School</option>
                  <option value="undergraduate">Undergraduate</option>
                  <option value="graduate">Graduate</option>
                  <option value="professional">Professional</option>
                </select>
              </div>
              
              <button 
                type="submit" 
                className="btn w-full mt-4"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating Research...
                  </span>
                ) : 'Generate Deep Research'}
              </button>
            </form>
          </div>
          
          {error && (
            <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-4 text-red-600 text-center">
              <p>{error}</p>
            </div>
          )}
          
          {content && (
            <div className="result-container mt-8">
              <h3 className="text-xl font-bold mb-4 text-primary-600">Research Content</h3>
              <div className="prose prose-slate max-w-none">
                {content.content.split('\n').map((paragraph, index) => (
                  <p key={index} className="mb-4">
                    {paragraph}
                  </p>
                ))}
              </div>
              
              {content.references && (
                <div className="mt-8 border-t border-gray-200 pt-6">
                  <h4 className="text-lg font-semibold mb-4 text-primary-600">References</h4>
                  <ul className="space-y-2 text-gray-700">
                    {content.references.map((reference, index) => (
                      <li key={index} className="pl-4 border-l-2 border-primary-200">
                        {reference}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
