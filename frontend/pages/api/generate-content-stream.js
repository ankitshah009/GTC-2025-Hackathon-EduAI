import { NextApiRequest, NextApiResponse } from 'next';

/**
 * API handler for generating streaming content.
 * This proxies the request to our backend API.
 */
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Set headers for streaming
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const { topic, audience } = req.body;

  if (!topic || !audience) {
    res.write(`data: ${JSON.stringify({ error: 'Missing required fields' })}\n\n`);
    res.end();
    return;
  }

  try {
    console.log(`Streaming content for topic: ${topic}, audience: ${audience}`);
    
    // Hard-code the backend API URL with IPv4
    const apiUrl = 'http://127.0.0.1:8000/api/content/generate/stream';
    
    console.log(`Making request to backend API: ${apiUrl}`);
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({ topic, audience }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend API error: ${response.status}`, errorText);
      res.write(`data: ${JSON.stringify({ error: `API error: ${response.status}` })}\n\n`);
      res.end();
      return;
    }

    // Read the response as a stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('Stream complete');
          res.write(`data: ${JSON.stringify({ finished: true })}\n\n`);
          res.end();
          break;
        }
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim() !== '');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            res.write(`data: ${data}\n\n`);
          }
        }
        
        // Flush the response to the client
        res.flush?.();
      }
    } catch (error) {
      console.error('Error processing stream:', error);
      res.write(`data: ${JSON.stringify({ error: 'Stream processing error' })}\n\n`);
      res.end();
    }
  } catch (error) {
    console.error('Error connecting to backend:', error);
    res.write(`data: ${JSON.stringify({ error: 'Failed to connect to backend' })}\n\n`);
    res.end();
  }
}
