from config.settings import Settings
from app.nvidia_api.llm_client import LLMClient
from typing import Dict, List, Any, Optional
import json
import re
import asyncio
import random

class DeepResearchService:
    """Service for deep educational research"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm_client = LLMClient(settings)
    
    async def generate_research(self, topic: str, subtopics: Optional[List[str]] = None, 
                               academic_level: str = "undergraduate", include_references: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive research on an educational topic.
        
        Args:
            topic: Main educational topic to research
            subtopics: Optional list of specific subtopics to focus on
            academic_level: Academic level (e.g., high school, undergraduate, graduate)
            include_references: Whether to include academic references
            
        Returns:
            Dictionary containing the research content
        """
        if self.settings.USE_MOCK_DATA:
            # For development/demo, return mock data
            return self._generate_mock_research(topic, subtopics, academic_level, include_references)
        
        # Construct prompt for the LLM
        prompt = self._create_research_prompt(topic, subtopics, academic_level, include_references)
        
        # Call NVIDIA's LLM API
        response = await self.llm_client.generate_text(prompt)
        
        # Parse the response to extract research content
        research_content = self._parse_research_response(response, topic, academic_level, include_references)
        
        return research_content
    
    async def get_trending_topics(self, academic_level: str = "undergraduate", limit: int = 10) -> List[Dict[str, str]]:
        """
        Get trending educational topics for research.
        
        Args:
            academic_level: Academic level filter
            limit: Maximum number of topics to return
            
        Returns:
            List of trending topics with descriptions
        """
        if self.settings.USE_MOCK_DATA:
            # For development/demo, return mock trending topics
            return self._generate_mock_trending_topics(academic_level, limit)
        
        # Construct prompt for the LLM
        prompt = f"""
        Generate a list of {limit} trending educational topics suitable for {academic_level} level research.
        
        For each topic, provide:
        1. The topic name
        2. A brief description (2-3 sentences)
        3. Why it's currently relevant or trending
        
        Format the response as a JSON array with objects containing "topic", "description", and "relevance" fields.
        """
        
        # Call NVIDIA's LLM API
        response = await self.llm_client.generate_text(prompt)
        
        # Parse the response to extract topics
        try:
            # Try to parse as JSON
            topics_data = json.loads(response)
            
            # Ensure we have the right structure
            if isinstance(topics_data, list) and all("topic" in item for item in topics_data):
                # Limit to requested number of topics
                return topics_data[:limit]
            else:
                # Fallback if structure is wrong
                return self._generate_mock_trending_topics(academic_level, limit)
        except:
            # Fallback if parsing fails
            return self._generate_mock_trending_topics(academic_level, limit)
    
    def _create_research_prompt(self, topic: str, subtopics: Optional[List[str]], academic_level: str, include_references: bool) -> str:
        """Create a prompt for the LLM to generate comprehensive research"""
        subtopics_text = ""
        if subtopics and len(subtopics) > 0:
            subtopics_text = "Focus on these specific subtopics:\n" + "\n".join([f"- {subtopic}" for subtopic in subtopics])
        
        references_text = "Include academic references in Chicago style at the end." if include_references else "Do not include references."
        
        return f"""
        Generate a comprehensive research document on "{topic}" suitable for {academic_level} level.
        
        {subtopics_text}
        
        The response should be structured as follows:
        
        1. INTRODUCTION: A detailed introduction to the topic
        
        2. SECTIONS: Multiple content sections covering key aspects of the topic
           Each section should have a clear title and comprehensive content
        
        3. KEY_CONCEPTS: A list of important concepts covered
        
        4. VISUALIZATION_PROMPTS: 3-5 detailed prompts for generating visualizations that would enhance understanding
        
        5. RELATED_TOPICS: 3-5 related topics with brief explanations of their relevance to the main topic
        
        {references_text}
        
        Format the response with clear section headings and detailed content for each section.
        The content should be academically rigorous and appropriate for {academic_level} level.
        """
    
    def _parse_research_response(self, response: str, topic: str, academic_level: str, include_references: bool) -> Dict[str, Any]:
        """
        Parse the LLM response to extract research content.
        
        Args:
            response: Raw response from the LLM
            topic: Original topic
            academic_level: Academic level requested
            include_references: Whether references were requested
            
        Returns:
            Structured research content
        """
        try:
            # Initialize default structure
            research_content = {
                "introduction": "",
                "sections": [],
                "references": [] if include_references else None,
                "related_topics": [],
                "key_concepts": [],
                "visualization_prompts": []
            }
            
            # Extract introduction
            intro_match = re.search(r"(?:INTRODUCTION:?|Introduction:?)(.*?)(?:SECTIONS|SECTION 1|Sections|Section 1|##)", response, re.DOTALL)
            if intro_match:
                research_content["introduction"] = intro_match.group(1).strip()
            else:
                # Fallback: use first paragraph as introduction
                paragraphs = response.split('\n\n')
                if paragraphs:
                    research_content["introduction"] = paragraphs[0].strip()
            
            # Extract sections
            # Look for sections with patterns like "SECTION: Title" or "## Title" or "Title\n---"
            section_matches = re.finditer(r"(?:SECTION \d+:?|Section \d+:?|##\s+|#\s+)(.*?)(?=(?:SECTION \d+:?|Section \d+:?|##\s+|#\s+|KEY_CONCEPTS|VISUALIZATION_PROMPTS|RELATED_TOPICS|REFERENCES|$))", response, re.DOTALL)
            
            for match in section_matches:
                section_text = match.group(0).strip()
                
                # Try to extract title and content
                title_match = re.match(r"(?:SECTION \d+:?|Section \d+:?|##\s+|#\s+)(.*?)(?:\n|\r\n)", section_text)
                if title_match:
                    title = title_match.group(1).strip()
                    content = section_text[title_match.end():].strip()
                    research_content["sections"].append({"title": title, "content": content})
            
            # Extract key concepts
            key_concepts_match = re.search(r"(?:KEY_CONCEPTS:?|Key Concepts:?)(.*?)(?:VISUALIZATION_PROMPTS|RELATED_TOPICS|REFERENCES|$)", response, re.DOTALL)
            if key_concepts_match:
                concepts_text = key_concepts_match.group(1).strip()
                # Extract bullet points
                concepts = [item.strip().lstrip('- ') for item in concepts_text.split('\n') if item.strip() and item.strip().startswith('-')]
                research_content["key_concepts"] = concepts
            
            # Extract visualization prompts
            viz_match = re.search(r"(?:VISUALIZATION_PROMPTS:?|Visualization Prompts:?)(.*?)(?:RELATED_TOPICS|REFERENCES|$)", response, re.DOTALL)
            if viz_match:
                viz_text = viz_match.group(1).strip()
                # Extract bullet points
                prompts = [item.strip().lstrip('- ') for item in viz_text.split('\n') if item.strip() and item.strip().startswith('-')]
                research_content["visualization_prompts"] = prompts
            
            # Extract related topics
            related_match = re.search(r"(?:RELATED_TOPICS:?|Related Topics:?)(.*?)(?:REFERENCES|$)", response, re.DOTALL)
            if related_match:
                related_text = related_match.group(1).strip()
                # Process each line that starts with a bullet or number
                for line in related_text.split('\n'):
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
                        # Extract topic and relevance if there's a colon or dash separating them
                        parts = re.split(r'[:\-–]', line.lstrip('- *0123456789.'), 1)
                        if len(parts) > 1:
                            research_content["related_topics"].append({
                                "topic": parts[0].strip(),
                                "relevance": parts[1].strip()
                            })
                        else:
                            # Just use the whole line as the topic
                            research_content["related_topics"].append({
                                "topic": parts[0].strip(),
                                "relevance": "Related area of study"
                            })
            
            # Extract references if requested
            if include_references:
                ref_match = re.search(r"(?:REFERENCES:?|References:?)(.*?)$", response, re.DOTALL)
                if ref_match:
                    ref_text = ref_match.group(1).strip()
                    # Split by line
                    ref_lines = [line.strip() for line in ref_text.split('\n') if line.strip()]
                    
                    # Process each reference
                    for ref in ref_lines:
                        if not ref or ref.startswith('-') or len(ref) < 10:
                            continue
                        
                        # Extract basic reference data
                        author_match = re.search(r'^([^\.]+)', ref)
                        title_match = re.search(r'"([^"]+)"', ref) or re.search(r'"([^"]+)"', ref)
                        year_match = re.search(r'\((\d{4})\)', ref) or re.search(r',\s*(\d{4})\b', ref)
                        doi_match = re.search(r'(10\.\d{4,}(?:\.\d+)*\/\S+)', ref)
                        url_match = re.search(r'(https?://\S+)', ref)
                        
                        # Construct reference object
                        reference = {
                            "title": title_match.group(1) if title_match else "Unknown title",
                            "authors": [a.strip() for a in author_match.group(1).split(',') if a.strip()] if author_match else ["Unknown author"],
                            "year": int(year_match.group(1)) if year_match else None,
                            "doi": doi_match.group(1) if doi_match else None,
                            "url": url_match.group(1) if url_match else None
                        }
                        
                        research_content["references"].append(reference)
            
            return research_content
            
        except Exception as e:
            # If parsing fails, return a default structure
            print(f"Error parsing research response: {str(e)}")
            return self._generate_mock_research(topic, None, academic_level, include_references)
    
    def _generate_mock_research(self, topic: str, subtopics: Optional[List[str]], academic_level: str, include_references: bool) -> Dict[str, Any]:
        """Generate mock research data for development and testing"""
        # Clean up topic and subtopics for use in the mock data
        topic_clean = topic.lower().strip()
        
        # Create some dynamic content based on the topic
        if "quantum" in topic_clean:
            field = "quantum physics"
            concepts = ["Quantum superposition", "Quantum entanglement", "Wave-particle duality", "Quantum tunneling"]
        elif "machine learning" in topic_clean or "ai" in topic_clean or "artificial intelligence" in topic_clean:
            field = "artificial intelligence"
            concepts = ["Neural networks", "Supervised learning", "Reinforcement learning", "Natural language processing"]
        elif "biology" in topic_clean or "genetic" in topic_clean:
            field = "biology"
            concepts = ["DNA structure", "Cell division", "Genetic inheritance", "Evolutionary theory"]
        elif "history" in topic_clean:
            field = "historical studies"
            concepts = ["Primary sources", "Historiography", "Cultural context", "Comparative analysis"]
        else:
            field = "academic research"
            concepts = ["Theoretical frameworks", "Empirical evidence", "Critical analysis", "Research methodologies"]
        
        # Introduction based on topic
        introduction = f"""
# Introduction to {topic.title()}

{topic.title()} is a fascinating area of study within {field}. This research explores the fundamental concepts, current developments, and future implications of {topic.lower()}. As an {academic_level} level exploration, this document covers both theoretical foundations and practical applications.

Understanding {topic.lower()} requires a multidisciplinary approach, drawing from various fields and methodologies. This research aims to provide a comprehensive overview while highlighting key areas of interest for further study.
        """
        
        # Create sections
        sections = [
            {
                "title": f"Theoretical Foundations of {topic.title()}",
                "content": f"""
This section explores the fundamental theories and principles that underpin {topic.lower()}.

The development of {topic.lower()} as a field of study has evolved significantly over time, with several key theoretical frameworks emerging. These frameworks provide the conceptual structure for understanding both basic phenomena and complex applications.

At the {academic_level} level, it's important to recognize how these theoretical foundations connect to practical implementations and real-world scenarios.
                """
            },
            {
                "title": f"Current Developments in {topic.title()}",
                "content": f"""
The field of {topic.lower()} has seen significant advancements in recent years.

Recent research has focused on expanding the applications and refining the methodologies associated with {topic.lower()}. These developments have led to new insights and capabilities that were previously unattainable.

For {academic_level} students, staying current with these developments provides valuable context for understanding the direction of the field and identifying promising areas for further study or research.
                """
            },
            {
                "title": f"Applications and Implications of {topic.title()}",
                "content": f"""
{topic.title()} has numerous practical applications across various domains.

From industry to academia, the principles and methodologies of {topic.lower()} are being applied to solve complex problems and create innovative solutions. These applications demonstrate the versatility and importance of {topic.lower()} in contemporary contexts.

The implications of these applications extend beyond technical considerations to include ethical, social, and policy dimensions that merit careful consideration at the {academic_level} level.
                """
            }
        ]
        
        # Add subtopic sections if provided
        if subtopics and len(subtopics) > 0:
            for subtopic in subtopics:
                sections.append({
                    "title": f"{subtopic.title()}: A Deeper Exploration",
                    "content": f"""
{subtopic.title()} represents a significant component of {topic.lower()} that warrants specific attention.

This subtopic encompasses various theoretical principles and practical applications that contribute to the broader understanding of {topic.lower()}. At the {academic_level} level, exploring {subtopic.lower()} provides valuable insights into specialized aspects of the field.

Recent developments in {subtopic.lower()} have expanded our understanding and opened new avenues for research and application.
                    """
                })
        
        # Visualization prompts
        viz_prompts = [
            f"Conceptual diagram showing the relationship between key components of {topic.lower()} with labeled elements and connections",
            f"Timeline visualization of the historical development of {topic.lower()} highlighting major milestones and breakthroughs",
            f"Comparative visualization showing different approaches or methodologies within {topic.lower()} with pros and cons of each",
            f"Process flow diagram illustrating how {topic.lower()} principles are applied in practical scenarios"
        ]
        
        # Related topics
        related_topics = [
            {
                "topic": f"Advanced {topic.title()} Methodologies",
                "relevance": f"Specialized techniques and approaches that extend basic {topic.lower()} concepts"
            },
            {
                "topic": f"Ethics in {topic.title()}",
                "relevance": f"Examination of ethical considerations and implications related to {topic.lower()}"
            },
            {
                "topic": f"Future Directions in {topic.title()}",
                "relevance": f"Emerging trends and potential developments in the field of {topic.lower()}"
            },
            {
                "topic": f"Interdisciplinary Applications of {topic.title()}",
                "relevance": f"How {topic.lower()} concepts are applied across different fields and disciplines"
            }
        ]
        
        # References if requested
        references = None
        if include_references:
            references = [
                {
                    "title": f"Fundamentals of {topic.title()}: Theory and Practice",
                    "authors": ["J. Smith", "A. Johnson"],
                    "publication": "Academic Press",
                    "year": 2022,
                    "doi": "10.1000/xyz123",
                    "url": None
                },
                {
                    "title": f"Recent Advances in {topic.title()}: A Comprehensive Review",
                    "authors": ["M. Williams", "S. Brown", "T. Davis"],
                    "publication": "Journal of Advanced Studies",
                    "year": 2023,
                    "doi": "10.1002/adv.202300042",
                    "url": None
                },
                {
                    "title": f"{topic.title()} in the Modern Context",
                    "authors": ["R. Miller"],
                    "publication": "Contemporary Research Press",
                    "year": 2021,
                    "doi": None,
                    "url": "https://example.com/research/publications/12345"
                }
            ]
        
        return {
            "introduction": introduction,
            "sections": sections,
            "references": references,
            "related_topics": related_topics,
            "key_concepts": concepts,
            "visualization_prompts": viz_prompts
        }
    
    def _generate_mock_trending_topics(self, academic_level: str, limit: int) -> List[Dict[str, str]]:
        """Generate mock trending topics for development and testing"""
        topics = [
            {
                "topic": "Quantum Machine Learning",
                "description": "The intersection of quantum computing and machine learning algorithms. This emerging field explores how quantum algorithms can accelerate or enhance traditional machine learning approaches.",
                "relevance": "Growing interest as quantum computing hardware advances and practical applications begin to emerge."
            },
            {
                "topic": "Zero-Knowledge Proofs",
                "description": "Cryptographic methods that allow one party to prove to another that a statement is true without revealing any additional information. ZKPs are fundamental to blockchain privacy and secure verification.",
                "relevance": "Increasingly important for privacy-preserving technologies and blockchain applications."
            },
            {
                "topic": "CRISPR Gene Editing Ethics",
                "description": "Ethical considerations surrounding the use of CRISPR-Cas9 and related gene editing technologies. Includes discussions of medical applications, ecological impacts, and governance frameworks.",
                "relevance": "Ongoing debates as gene editing technologies become more accessible and powerful."
            },
            {
                "topic": "Climate Adaptation Strategies",
                "description": "Approaches for adapting to climate change impacts across different sectors and regions. Includes both technological solutions and policy frameworks.",
                "relevance": "Urgent relevance as climate change impacts become more severe and widespread."
            },
            {
                "topic": "Synthetic Biology Applications",
                "description": "The design and construction of new biological entities for practical purposes. Encompasses biofuels, medicine, materials science, and environmental remediation.",
                "relevance": "Rapid advancement of tools and techniques enabling new applications."
            },
            {
                "topic": "Neuromorphic Computing",
                "description": "Computing systems that mimic the architecture and principles of the human brain. These systems aim to achieve greater efficiency and capability for certain types of computational tasks.",
                "relevance": "Growing interest as AI capabilities expand and traditional computing approaches reach physical limitations."
            },
            {
                "topic": "Circular Economy Models",
                "description": "Economic systems designed to eliminate waste and continually reuse resources. Encompasses product design, supply chain management, and business model innovation.",
                "relevance": "Increasing adoption as sustainability becomes a priority for businesses and governments."
            },
            {
                "topic": "Extended Reality in Education",
                "description": "The use of virtual reality (VR), augmented reality (AR), and mixed reality (MR) technologies in educational contexts. Includes both theoretical frameworks and practical implementations.",
                "relevance": "Expanding rapidly as XR technologies become more accessible and educational institutions seek innovative approaches."
            },
            {
                "topic": "Algorithmic Fairness",
                "description": "The study and implementation of algorithms that avoid bias and discrimination. Encompasses technical approaches, ethical frameworks, and policy considerations.",
                "relevance": "Critical importance as algorithms increasingly influence high-stakes decisions in society."
            },
            {
                "topic": "Sustainable Urban Planning",
                "description": "Approaches to designing cities that meet environmental, social, and economic sustainability goals. Includes transportation systems, energy infrastructure, and building design.",
                "relevance": "Growing urgency as urbanization continues and cities face environmental and social challenges."
            },
            {
                "topic": "Blockchain Governance",
                "description": "Mechanisms for decision-making and conflict resolution in blockchain systems. Includes both on-chain governance processes and off-chain social and institutional arrangements.",
                "relevance": "Increasingly important as blockchain systems become more complex and widely adopted."
            },
            {
                "topic": "Quantum Sensing Technologies",
                "description": "The use of quantum systems for highly sensitive measurements. Applications include gravitational field mapping, magnetic field detection, and precise timing.",
                "relevance": "Emerging practical applications with significant potential impact across multiple fields."
            }
        ]
        
        # Filter by academic level
        if academic_level.lower() == "high school":
            # Simplify descriptions for high school level
            for topic in topics:
                sentences = topic["description"].split(". ")
                if len(sentences) > 1:
                    topic["description"] = sentences[0] + "."
        
        # Randomly select the requested number of topics (but ensure consistency for the same input)
        seed = sum(ord(c) for c in academic_level)
        random.seed(seed)
        return random.sample(topics, min(limit, len(topics)))