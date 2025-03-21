import React, { useState } from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';

export default function ContentGenerator() {
  const [topic, setTopic] = useState('');
  const [audience, setAudience] = useState('middle-school');
  const [contentType, setContentType] = useState('lesson-plan');
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/generate-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          audience,
          contentType,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate content');
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
        <title>Content Generator | EduAI</title>
        <meta name="description" content="Generate tailored educational content with AI" />
      </Head>
      
      <div className="container py-8">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4" style={{ color: '#5e35b1' }}>Educational Content Generator</h1>
            <p className="text-gray-600">Create customized educational content for any grade level or subject area.</p>
          </div>
          
          <div className="card">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="topic" className="form-label">Topic</label>
                <input
                  id="topic"
                  type="text"
                  className="form-input"
                  placeholder="e.g. Photosynthesis, American Civil War, Pythagorean Theorem"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  required
                />
              </div>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div className="form-group">
                  <label htmlFor="audience" className="form-label">Target Audience</label>
                  <select
                    id="audience"
                    className="form-select"
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                  >
                    <option value="elementary">Elementary School</option>
                    <option value="middle-school">Middle School</option>
                    <option value="high-school">High School</option>
                    <option value="undergraduate">Undergraduate</option>
                    <option value="graduate">Graduate</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label htmlFor="contentType" className="form-label">Content Type</label>
                  <select
                    id="contentType"
                    className="form-select"
                    value={contentType}
                    onChange={(e) => setContentType(e.target.value)}
                  >
                    <option value="lesson-plan">Lesson Plan</option>
                    <option value="quiz">Quiz Questions</option>
                    <option value="summary">Topic Summary</option>
                    <option value="activity">Interactive Activity</option>
                  </select>
                </div>
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
                    Generating...
                  </span>
                ) : 'Generate Content'}
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
              <h3 className="text-xl font-bold mb-4 text-primary-600">Generated Content</h3>
              <div className="prose prose-slate max-w-none">
                {content.content.split('\n').map((paragraph, index) => (
                  <p key={index} className="mb-4">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}