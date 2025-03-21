import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function ContentGenerator() {
  const [topic, setTopic] = useState('');
  const [audience, setAudience] = useState('middle-school');
  const [contentType, setContentType] = useState('lesson-plan');
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState(null);
  const [error, setError] = useState(null);
  const [generatingImage, setGeneratingImage] = useState(false);
  const [generatedImages, setGeneratedImages] = useState({});
  const [imageError, setImageError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setContent(null);
    setGeneratedImages({});
    
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
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate content');
      }
      
      const data = await response.json();
      setContent(data);
      
      // Auto-generate images if there are prompts
      if (data.imagePrompts && data.imagePrompts.length > 0) {
        // Generate the first image immediately
        handleGenerateImage(data.imagePrompts[0]);
      }
    } catch (err) {
      console.error('Error in content generation:', err);
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateImage = async (prompt) => {
    setGeneratingImage(true);
    setImageError(null);
    
    try {
      console.log(`Generating image for prompt: ${prompt}`);
      const response = await fetch('/api/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });
      
      // Check if the response is OK first
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response from API:', response.status, errorText);
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }
      
      // Parse response JSON - clone response to avoid "body already read" error
      const data = await response.clone().json().catch(e => {
        console.error('JSON parsing error:', e);
        throw new Error('Failed to parse API response');
      });
      
      console.log('Received image generation response:', data);
      
      if (data && data.success) {
        console.log(`Successfully generated image with URL: ${data.image_url}`);
        
        // Verify we have a valid image URL
        if (!data.image_url) {
          throw new Error('No image URL returned from API');
        }
        
        // Immediately update state with the image URL
        setGeneratedImages(prevState => ({
          ...prevState,
          [prompt]: data.image_url
        }));
      } else {
        const errorMsg = data?.error || 'Failed to generate image';
        console.error('API reported failure:', errorMsg);
        throw new Error(errorMsg);
      }
    } catch (err) {
      console.error('Error in image generation:', err);
      setImageError(err.message || 'Failed to generate image');
    } finally {
      setGeneratingImage(false);
    }
  };

  // Add this useEffect to automatically generate all images when content changes
  useEffect(() => {
    const generateAllImages = async () => {
      if (content && content.imagePrompts && content.imagePrompts.length > 0) {
        // Generate all images in sequence
        for (const prompt of content.imagePrompts) {
          if (!generatedImages[prompt]) {
            await handleGenerateImage(prompt);
          }
        }
      }
    };
    
    generateAllImages();
  }, [content]);

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
              <div className="prose prose-slate max-w-none bg-white border border-gray-200 rounded-lg p-6">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {content.content}
                </ReactMarkdown>
              </div>
              
              {content.imagePrompts && content.imagePrompts.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-lg font-semibold mb-2">Generated Images</h4>
                  <div className="bg-yellow-50 border border-yellow-200 p-4 mb-4 rounded-lg">
                    <p className="text-sm text-yellow-700">Debug info - Images to generate: {content.imagePrompts.length}, Images generated: {Object.keys(generatedImages).length}</p>
                  </div>
                  <ul className="list-disc pl-5 space-y-6">
                    {content.imagePrompts.map((prompt, index) => (
                      <li key={index} className="text-gray-700">
                        <div className="flex flex-col space-y-2">
                          <p className="font-medium">Prompt #{index + 1}</p>
                          {generatedImages[prompt] ? (
                            <div className="mt-2">
                              <p className="text-xs text-blue-600 mb-1">Image URL: {generatedImages[prompt]}</p>
                              <div className="border border-gray-200 rounded shadow-md p-2 overflow-hidden">
                                <img 
                                  src={generatedImages[prompt]} 
                                  alt={`Generated image for: ${prompt}`}
                                  width={600}
                                  height={400}
                                  loading="lazy"
                                  className="max-w-full h-auto rounded"
                                  onError={(e) => {
                                    console.error('Failed to load image:', e.target.src);
                                    e.target.onerror = null; 
                                    e.target.src = 'https://via.placeholder.com/400x300?text=Image+Load+Error';
                                    e.target.className += ' border-red-500';
                                  }}
                                />
                              </div>
                              <p className="text-sm text-gray-500 mt-1">{prompt}</p>
                            </div>
                          ) : (
                            <div className="flex flex-col space-y-2">
                              <p className="text-sm">{prompt}</p>
                              <button
                                className="self-start px-3 py-1 bg-primary-600 text-white text-sm rounded hover:bg-primary-700 transition-colors"
                                onClick={() => handleGenerateImage(prompt)}
                                disabled={generatingImage}
                              >
                                {generatingImage ? 'Generating...' : 'Generate Image'}
                              </button>
                            </div>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                  
                  {imageError && (
                    <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-600">
                      <p>{imageError}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}