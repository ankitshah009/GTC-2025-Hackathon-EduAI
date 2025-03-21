export default async function handler(req, res) {
  // Handle HEAD requests as well as GET
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Get the image path from the query
    const { imagePath } = req.query;
    
    if (!imagePath) {
      console.error('Missing imagePath parameter');
      return res.status(400).json({ error: 'Missing imagePath parameter' });
    }

    // Create the full image URL
    const backendBaseUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
    const imageUrl = `${backendBaseUrl}${imagePath}`;
    
    console.log(`Proxying image from: ${imageUrl}`);

    // Fetch the image from the backend with a timeout
    let fetchOptions = {
      method: req.method, // Use the same method as the incoming request
      timeout: 15000,     // 15 second timeout
      headers: {
        'Accept': 'image/*, */*'
      }
    };

    let response;
    try {
      response = await fetch(imageUrl, fetchOptions);
    } catch (fetchError) {
      console.error(`Network error fetching image: ${fetchError.message}`);
      // Return a fallback image instead of an error
      res.setHeader('Content-Type', 'image/png');
      res.setHeader('Cache-Control', 'public, max-age=86400');
      // Redirect to a placeholder image service
      return res.redirect(302, 'https://via.placeholder.com/400x300?text=Image+Unavailable');
    }
    
    if (!response.ok) {
      console.error(`Failed to fetch image: ${response.status} ${response.statusText}`);
      // Return a fallback image instead of an error
      res.setHeader('Content-Type', 'image/png');
      res.setHeader('Cache-Control', 'public, max-age=86400');
      // Redirect to a placeholder image service
      return res.redirect(302, 'https://via.placeholder.com/400x300?text=Image+Unavailable');
    }

    // Get the content type from the response
    const contentType = response.headers.get('content-type') || 'image/png';
    
    // If it's a HEAD request, just send the headers
    if (req.method === 'HEAD') {
      res.setHeader('Content-Type', contentType);
      return res.status(200).end();
    }
    
    // Get the image data as a buffer
    let imageBuffer;
    try {
      imageBuffer = await response.arrayBuffer();
    } catch (bufferError) {
      console.error(`Error reading image data: ${bufferError.message}`);
      // Return a fallback image
      res.setHeader('Content-Type', 'image/png');
      res.setHeader('Cache-Control', 'public, max-age=86400');
      return res.redirect(302, 'https://via.placeholder.com/400x300?text=Image+Data+Error');
    }
    
    // Set the appropriate headers
    res.setHeader('Content-Type', contentType);
    res.setHeader('Cache-Control', 'public, max-age=86400'); // Cache for 24 hours
    
    // Send the image data
    res.status(200).send(Buffer.from(imageBuffer));
  } catch (error) {
    console.error('Error proxying image:', error);
    // Return a fallback image instead of an error
    res.setHeader('Content-Type', 'image/png');
    res.setHeader('Cache-Control', 'public, max-age=86400');
    return res.redirect(302, 'https://via.placeholder.com/400x300?text=Error');
  }
}
