from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DeepResearchRequest(BaseModel):
    """Request model for deep research on educational topics"""
    topic: str = Field(..., description="Educational topic to research in depth")
    subtopics: Optional[List[str]] = Field(None, description="Specific subtopics to research (optional)")
    academic_level: str = Field(..., description="Academic level (e.g., high school, undergraduate, graduate)")
    include_references: bool = Field(True, description="Whether to include academic references")
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "quantum computing",
                "subtopics": ["quantum entanglement", "quantum algorithms", "quantum error correction"],
                "academic_level": "undergraduate",
                "include_references": True
            }
        }

class ResearchSection(BaseModel):
    """Model for a section of research content"""
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content in markdown format")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Quantum Entanglement",
                "content": "Quantum entanglement is a physical phenomenon that occurs when pairs or groups of particles..."
            }
        }

class AcademicReference(BaseModel):
    """Model for an academic reference"""
    title: str = Field(..., description="Title of the referenced work")
    authors: List[str] = Field(..., description="List of authors")
    publication: Optional[str] = Field(None, description="Publication name/journal")
    year: Optional[int] = Field(None, description="Publication year")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    url: Optional[str] = Field(None, description="URL to the reference (if available)")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Quantum Computing in the NISQ era and beyond",
                "authors": ["John Preskill"],
                "publication": "Quantum",
                "year": 2018,
                "doi": "10.22331/q-2018-08-06-79",
                "url": "https://quantum-journal.org/papers/q-2018-08-06-79/"
            }
        }

class RelatedTopic(BaseModel):
    """Model for a related topic suggestion"""
    topic: str = Field(..., description="Related topic name")
    relevance: str = Field(..., description="Brief explanation of relevance to the main topic")
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "Quantum Cryptography",
                "relevance": "Applications of quantum computing principles for secure communication"
            }
        }

class DeepResearchResponse(BaseModel):
    """Response model for deep research"""
    introduction: str = Field(..., description="Introduction to the topic in markdown format")
    sections: List[ResearchSection] = Field(..., description="Main content sections")
    references: Optional[List[AcademicReference]] = Field(None, description="Academic references")
    related_topics: List[RelatedTopic] = Field(..., description="Suggested related topics for further research")
    key_concepts: List[str] = Field(..., description="List of key concepts covered")
    visualization_prompts: List[str] = Field(..., description="Prompts for generating visualizations")
    
    class Config:
        schema_extra = {
            "example": {
                "introduction": "Quantum computing is a rapidly evolving field that leverages quantum mechanical phenomena...",
                "sections": [
                    {
                        "title": "Quantum Bits (Qubits)",
                        "content": "Unlike classical bits which can only be in states 0 or 1, quantum bits or qubits..."
                    }
                ],
                "references": [
                    {
                        "title": "Quantum Computing in the NISQ era and beyond",
                        "authors": ["John Preskill"],
                        "publication": "Quantum",
                        "year": 2018,
                        "doi": "10.22331/q-2018-08-06-79"
                    }
                ],
                "related_topics": [
                    {
                        "topic": "Quantum Cryptography",
                        "relevance": "Applications of quantum computing principles for secure communication"
                    }
                ],
                "key_concepts": ["Quantum superposition", "Quantum entanglement", "Quantum gates"],
                "visualization_prompts": [
                    "Diagram showing the difference between classical bits and qubits"
                ]
            }
        }
