export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Missing prompt field' });
    }

    // Call the backend Gemini image generation API
    const apiUrl = 'http://127.0.0.1:8000/api/images/generate-gemini';
    
    console.log(`Making request to backend image API: ${apiUrl}`);
    console.log(`Prompt: ${prompt}`);
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    // Handle API response
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend image API error: ${response.status}`, errorText);
      throw new Error(`API error: ${response.status}`);
    }

    // Parse the response data
    const data = await response.json();
    console.log('Received image data from backend:', data);

    // Return the image URL to the frontend
    return res.status(200).json({
      success: true,
      image_url: data.image_url,
      error: null
    });
  } catch (error) {
    console.error('Error generating image:', error);
    return res.status(500).json({ 
      success: false,
      image_url: null,
      error: error.message || 'Failed to generate image' 
    });
  }
} 