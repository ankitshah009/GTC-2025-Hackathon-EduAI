export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { topic, audience, contentType } = req.body;

    if (!topic || !audience || !contentType) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // For now, return a mock response
    // In a real implementation, you would call your backend API here
    const mockContent = generateMockContent(topic, audience, contentType);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    return res.status(200).json({
      content: mockContent
    });
  } catch (error) {
    console.error('Error generating content:', error);
    return res.status(500).json({ error: 'Failed to generate content' });
  }
}

function generateMockContent(topic, audience, contentType) {
  let content = '';
  
  if (contentType === 'lesson-plan') {
    content = `# Lesson Plan: ${topic}\n\n` +
      `## Target Audience: ${audience}\n\n` +
      `## Objectives:\n` +
      `- Students will understand key concepts related to ${topic}\n` +
      `- Students will be able to explain the importance of ${topic}\n` +
      `- Students will demonstrate knowledge through activities\n\n` +
      `## Introduction (10 minutes):\n` +
      `Begin the lesson by asking students what they already know about ${topic}. Write their responses on the board and discuss any misconceptions.\n\n` +
      `## Main Content (25 minutes):\n` +
      `Present the key concepts of ${topic} using visual aids and examples relevant to ${audience} students.\n\n` +
      `## Activity (15 minutes):\n` +
      `Have students work in small groups to create a concept map showing the relationships between different aspects of ${topic}.\n\n` +
      `## Assessment:\n` +
      `Students will complete a short quiz to demonstrate their understanding of ${topic}.`;
  } else if (contentType === 'quiz') {
    content = `# Quiz Questions on ${topic}\n\n` +
      `1. What is the primary function of ${topic}?\n` +
      `   a) First option\n` +
      `   b) Second option\n` +
      `   c) Third option\n` +
      `   d) Fourth option\n\n` +
      `2. How does ${topic} relate to wider concepts in this field?\n` +
      `   a) First connection\n` +
      `   b) Second connection\n` +
      `   c) Third connection\n` +
      `   d) Fourth connection\n\n` +
      `3. In what year was ${topic} first discovered or developed?\n` +
      `   a) Year one\n` +
      `   b) Year two\n` +
      `   c) Year three\n` +
      `   d) Year four\n\n` +
      `4. Who is considered the leading expert on ${topic}?\n` +
      `   a) Person one\n` +
      `   b) Person two\n` +
      `   c) Person three\n` +
      `   d) Person four\n\n` +
      `5. What is a common misconception about ${topic}?\n` +
      `   a) Misconception one\n` +
      `   b) Misconception two\n` +
      `   c) Misconception three\n` +
      `   d) Misconception four`;
  } else {
    content = `# ${topic}\n\n` +
      `## Introduction\n` +
      `${topic} is a fascinating subject with many applications and implications. This content is tailored for ${audience} level students to provide a comprehensive understanding of the topic.\n\n` +
      `## Key Concepts\n` +
      `When studying ${topic}, it's important to understand several fundamental principles:\n\n` +
      `1. The first principle relates to the core definition and scope of ${topic}.\n` +
      `2. The second principle examines how ${topic} functions in various contexts.\n` +
      `3. The third principle explores the historical development of ${topic} and its evolution over time.\n\n` +
      `## Applications\n` +
      `${topic} has numerous real-world applications, including:\n\n` +
      `- Application in educational settings\n` +
      `- Practical use in industry\n` +
      `- Relevance to current research and development\n\n` +
      `## Conclusion\n` +
      `Understanding ${topic} provides valuable insights and skills that are applicable across multiple disciplines. Further exploration is encouraged to deepen knowledge in this area.`;
  }
  
  return content;
} 