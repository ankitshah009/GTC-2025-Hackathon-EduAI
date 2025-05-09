/**
 * Streaming Demo - Shows how to use the streaming API for content generation
 * 
 * This example demonstrates how to connect to the streaming endpoint and
 * receive text chunks as they are generated by the LLM.
 */

async function generateContentStream(topic, audience) {
  // Container to display the streaming content
  const contentContainer = document.getElementById('content-container');
  const statusEl = document.getElementById('status');
  
  // Clear previous content
  contentContainer.innerHTML = '';
  statusEl.textContent = 'Generating content...';
  
  try {
    // Prepare the request payload
    const payload = {
      topic,
      audience
    };
    
    // Connect to the streaming endpoint
    const response = await fetch('http://localhost:8000/api/content/generate/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });
    
    // Check if the response is ok
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // Get the response reader for streaming
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let imagePrompts = [];
    
    // Read chunks as they arrive
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // Decode the chunk
      const chunk = decoder.decode(value);
      
      // Process each event (each event starts with "data: ")
      const events = chunk.split('\n\n');
      
      for (const event of events) {
        if (event.startsWith('data: ')) {
          try {
            // Parse the JSON data
            const jsonData = JSON.parse(event.slice(5));
            
            if (jsonData.error) {
              throw new Error(jsonData.error);
            }
            
            if (jsonData.finished) {
              // Last chunk with image prompts
              statusEl.textContent = 'Content generation complete!';
              imagePrompts = jsonData.image_prompts || [];
              
              // Display the image prompts
              if (imagePrompts.length > 0) {
                const imagePromptsContainer = document.createElement('div');
                imagePromptsContainer.className = 'image-prompts-container';
                imagePromptsContainer.innerHTML = '<h3>Image Prompts:</h3>';
                
                const list = document.createElement('ul');
                for (const prompt of imagePrompts) {
                  const item = document.createElement('li');
                  item.textContent = prompt;
                  list.appendChild(item);
                }
                
                imagePromptsContainer.appendChild(list);
                contentContainer.appendChild(imagePromptsContainer);
              }
            } else {
              // Regular content chunk
              contentContainer.innerHTML += jsonData.chunk;
              
              // Auto-scroll to bottom to follow the content generation
              contentContainer.scrollTop = contentContainer.scrollHeight;
            }
          } catch (error) {
            console.error('Error parsing SSE event:', error);
          }
        }
      }
    }
    
  } catch (error) {
    console.error('Error:', error);
    statusEl.textContent = `Error: ${error.message}`;
  }
}

// Example usage
document.getElementById('generate-btn').addEventListener('click', () => {
  const topic = document.getElementById('topic-input').value;
  const audience = document.getElementById('audience-select').value;
  
  if (!topic) {
    alert('Please enter a topic');
    return;
  }
  
  generateContentStream(topic, audience);
});
