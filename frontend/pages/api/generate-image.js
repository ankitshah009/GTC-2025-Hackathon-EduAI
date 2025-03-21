export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ 
        success: false,
        image_url: null,
        error: 'Missing prompt field' 
      });
    }

    // Call the backend Gemini image generation API
    // Always use IPv4 (127.0.0.1) instead of localhost to avoid IPv6 issues
    const backendBaseUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
    const apiUrl = `${backendBaseUrl}/api/images/generate-gemini`;
    
    console.log(`Making request to backend image API: ${apiUrl}`);
    console.log(`Prompt: ${prompt}`);
    
    // Make the request with proper error handling
    let response;
    try {
      response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });
    } catch (fetchError) {
      console.error(`Network error calling backend: ${fetchError.message}`);
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

    // Use our proxy instead of direct backend URL
    // This prevents CORS issues when loading images from another domain
    const proxyUrl = `/api/proxy-image?imagePath=${encodeURIComponent(data.image_url)}`;
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