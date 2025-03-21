import { NextApiRequest, NextApiResponse } from 'next';

/**
 * API handler for generating streaming content.
 * This proxies the request to our backend API.
 */
export default async function handler(req, res) {
  // Only accept POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Get request data
    const { topic, audience } = req.body;
    
    if (!topic || !audience) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    // Set up headers for server-sent events
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    // Get backend API URL from environment variables or use default
    const apiUrl = `${process.env.BACKEND_API_URL || 'http://localhost:8000'}/api/content/generate/stream`;
    
    console.log(`Proxying streaming request to: ${apiUrl}`);
    
    // Make API request to backend
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ topic, audience }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend API error: ${response.status}`, errorText);
      res.write(`data: ${JSON.stringify({ error: `API error: ${response.status}` })}\n\n`);
      return res.end();
    }
    
    // Stream the response from the backend to the client
    const reader = response.body.getReader();
    
    async function streamResponse() {
      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            return res.end();
          }
          
          // Forward the chunk directly
          const chunk = new TextDecoder().decode(value);
          res.write(chunk);
          
          // Flush the response to ensure it's sent immediately
          if (res.flush) {
            res.flush();
          }
        }
      } catch (error) {
        console.error('Error streaming response:', error);
        res.write(`data: ${JSON.stringify({ error: 'Error streaming response' })}\n\n`);
        res.end();
      }
    }
    
    await streamResponse();
    
  } catch (error) {
    console.error('API handler error:', error);
    res.write(`data: ${JSON.stringify({ error: error.message || 'An unexpected error occurred' })}\n\n`);
    res.end();
  }
}
