import fetch from 'node-fetch';

export default async function handler(req, res) {
  // Handle HEAD requests as well as GET
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Get the image path from the query parameters
  const { imagePath } = req.query;
  
  if (!imagePath) {
    console.error('Missing imagePath parameter');
    return res.status(400).json({ error: 'Missing imagePath parameter' });
  }

  // Remove any query parameters from the image path
  const cleanImagePath = imagePath.split('?')[0];
  console.log('Removed query parameters from image path:', cleanImagePath);

  try {
    // Construct the full URL to the image on the backend
    const backendBaseUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
    const imageUrl = `${backendBaseUrl}${cleanImagePath}`;
    
    console.log('Proxying image from:', imageUrl);
    
    // Add cache busting parameter
    const cacheBuster = `?t=${Date.now()}`;
    const cacheBustedUrl = `${imageUrl}${cacheBuster}`;
    console.log('Adding cache busting parameter:', cacheBustedUrl);

    // Fetch the image with a timeout
    const response = await fetch(cacheBustedUrl, {
      method: req.method, // Use the same method as the incoming request
      timeout: 15000 // 15 second timeout
    });

    if (!response.ok) {
      console.error(`Error fetching image: ${response.status} ${response.statusText}`);
      return res.status(response.status).json({ 
        error: `Failed to fetch image: ${response.status} ${response.statusText}` 
      });
    }

    // Get the content type from the response
    const contentType = response.headers.get('content-type');
    console.log('Content-Type from backend:', contentType);
    
    // If it's a HEAD request, just send the headers
    if (req.method === 'HEAD') {
      res.setHeader('Content-Type', contentType || 'image/png');
      return res.status(200).end();
    }
    
    // Set appropriate headers
    res.setHeader('Content-Type', contentType || 'image/png');
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
    
    // Get the image data as a buffer
    const imageData = await response.arrayBuffer();
    console.log(`Successfully retrieved image data: ${imageData.byteLength} bytes`);
    
    // Validate image data (basic check)
    if (imageData.byteLength < 100) {
      console.error(`Suspiciously small image data: ${imageData.byteLength} bytes`);
      return res.status(500).json({ error: 'Invalid image data received' });
    }
    
    // Send the image data
    res.status(200).send(Buffer.from(imageData));
  } catch (error) {
    console.error('Error proxying image:', error.message);
    res.status(500).json({ 
      error: `Failed to proxy image: ${error.message}`,
      imagePath: cleanImagePath
    });
  }
}

// Helper function to serve error placeholder images
function serveErrorImage(res, errorType = 'Error') {
  console.log(`Serving error image for: ${errorType}`);
  res.setHeader('Content-Type', 'image/png');
  res.setHeader('Cache-Control', 'public, max-age=60'); // Short cache for errors
  return res.redirect(302, `https://via.placeholder.com/400x300?text=Image+${errorType.replace(/\s+/g, '+')}`);
}
