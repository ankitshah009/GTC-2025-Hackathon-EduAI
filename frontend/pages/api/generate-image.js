import fetch from 'node-fetch';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false, 
      error: 'Method not allowed' 
    });
  }

  // Get the prompt from the request body
  const { prompt, timestamp } = req.body;
  
  if (!prompt) {
    console.error('Missing prompt in request body');
    return res.status(400).json({ 
      success: false, 
      image_url: null, 
      error: 'Missing prompt' 
    });
  }

  console.log(`Making request to backend image API: ${process.env.BACKEND_API_URL || 'http://127.0.0.1:8000'}/api/images/generate-gemini`);
  console.log(`Prompt: ${prompt}`);
  
  try {
    const backendBaseUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
    
    // Make the request to the backend with a timeout
    let response;
    try {
      response = await fetch(`${backendBaseUrl}/api/images/generate-gemini`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: prompt,
          timestamp: timestamp || Date.now()
        }),
        timeout: 30000 // 30 second timeout
      });
    } catch (fetchError) {
      console.error(`Network error: ${fetchError.message}`);
      return res.status(500).json({
        success: false,
        image_url: null,
        error: `Network error: ${fetchError.message}`
      });
    }

    // Handle API response
    if (!response.ok) {
      let errorMessage;
      try {
        const errorData = await response.text();
        errorMessage = errorData;
        console.error(`Backend image API error: ${response.status}`, errorData);
      } catch (textError) {
        errorMessage = `Status ${response.status}`;
        console.error(`Backend image API error: ${response.status}, failed to get error details`);
      }
      
      return res.status(response.status).json({
        success: false,
        image_url: null,
        error: `API error: ${errorMessage}`
      });
    }

    // Parse the response data
    let data;
    try {
      data = await response.json();
      console.log('Received image data from backend:', data);
    } catch (jsonError) {
      console.error(`Failed to parse backend response as JSON: ${jsonError.message}`);
      return res.status(500).json({
        success: false,
        image_url: null,
        error: 'Invalid JSON response from backend'
      });
    }

    // Validate the data
    if (!data || !data.image_url) {
      console.error('Backend returned success but no image URL');
      return res.status(500).json({
        success: false,
        image_url: null,
        error: 'Backend did not return an image URL'
      });
    }

    // Add a random query string to prevent caching
    const cacheBuster = `?t=${Date.now()}&r=${Math.random().toString(36).substring(7)}`;
    
    // Use our proxy instead of direct backend URL
    // This prevents CORS issues when loading images from another domain
    const proxyUrl = `/api/proxy-image?imagePath=${encodeURIComponent(data.image_url)}${cacheBuster}`;
    console.log('Proxied image URL:', proxyUrl);

    // Return the proxied image URL to the frontend
    return res.status(200).json({
      success: true,
      image_url: proxyUrl,
      original_url: `${backendBaseUrl}${data.image_url}`, // Keep original for debugging
      error: null
    });
  } catch (error) {
    console.error('Unhandled error generating image:', error);
    return res.status(500).json({ 
      success: false,
      image_url: null,
      error: error.message || 'An unexpected error occurred' 
    });
  }
}