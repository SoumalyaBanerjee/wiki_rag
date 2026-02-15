"""Citation Manager for tracking and formatting sources."""

from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Citation:
    """Represents a single citation."""
    title: str
    source_url: str
    score: float
    citation_type: str = "text"  # "text" or "image"
    snippet: Optional[str] = None
    image_name: Optional[str] = None
    
    def __hash__(self):
        """Make citation hashable for deduplication."""
        return hash((self.title, self.source_url))
    
    def __eq__(self, other):
        """Check equality for deduplication."""
        if not isinstance(other, Citation):
            return False
        return (self.title == other.title and 
                self.source_url == other.source_url)


class CitationManager:
    """
    Manages citations from search results.
    
    Features:
    - Track text and image sources
    - Automatic deduplication
    - Formatted output for display
    - Bibliography generation
    """
    
    def __init__(self):
        """Initialize citation manager."""
        self.citations: Dict[str, Citation] = {}
        self._counter = 1
    
    def add_text_citation(
        self, 
        title: str, 
        source_url: str, 
        score: float, 
        snippet: Optional[str] = None
    ) -> None:
        """
        Add a text citation from search results.
        
        Args:
            title: Article/document title
            source_url: Source URL
            score: Relevance score (0-1)
            snippet: Optional text snippet
        """
        key = f"{title}:{source_url}"
        
        # Skip if already exists (deduplication)
        if key in self.citations:
            # Update score if higher
            if score > self.citations[key].score:
                self.citations[key].score = score
            return
        
        citation = Citation(
            title=title,
            source_url=source_url,
            score=score,
            citation_type="text",
            snippet=snippet
        )
        self.citations[key] = citation
    
    def add_image_citation(
        self, 
        image_name: str, 
        image_path: str, 
        score: float
    ) -> None:
        """
        Add an image citation from search results.
        
        Args:
            image_name: Name/title of image
            image_path: Path or MinIO bucket path
            score: Relevance score (0-1)
        """
        key = f"image:{image_name}:{image_path}"
        
        if key in self.citations:
            if score > self.citations[key].score:
                self.citations[key].score = score
            return
        
        citation = Citation(
            title=image_name,
            source_url=image_path,
            score=score,
            citation_type="image",
            image_name=image_name
        )
        self.citations[key] = citation
    
    def format_citations(self, max_citations: int = 10) -> List[str]:
        """
        Return formatted citation list for display.
        
        Format: "[1] Title (Score: 0.92) - URL"
        
        Args:
            max_citations: Maximum number of citations to return
            
        Returns:
            List of formatted citation strings
        """
        # Sort by score descending
        sorted_citations = sorted(
            self.citations.values(),
            key=lambda c: c.score,
            reverse=True
        )[:max_citations]
        
        formatted = []
        for idx, citation in enumerate(sorted_citations, 1):
            score_text = f" (Score: {citation.score:.2f})"
            formatted_str = f"[{idx}] {citation.title}{score_text}\n    {citation.source_url}"
            
            if citation.snippet:
                formatted_str += f"\n    Snippet: {citation.snippet[:100]}..."
            
            formatted.append(formatted_str)
        
        return formatted
    
    def format_citations_inline(self) -> List[str]:
        """
        Return inline citations for use in text.
        
        Format: "[1] Title (0.92)"
        
        Returns:
            List of inline citation strings
        """
        sorted_citations = sorted(
            self.citations.values(),
            key=lambda c: c.score,
            reverse=True
        )
        
        return [
            f"[{idx}] {c.title} ({c.score:.2f})"
            for idx, c in enumerate(sorted_citations, 1)
        ]
    
    def get_bibliography(self) -> str:
        """
        Return formatted bibliography.
        
        Returns:
            Markdown-formatted bibliography
        """
        sorted_citations = sorted(
            self.citations.values(),
            key=lambda c: c.score,
            reverse=True
        )
        
        if not sorted_citations:
            return "No citations."
        
        lines = ["## Sources\n"]
        
        for idx, citation in enumerate(sorted_citations, 1):
            lines.append(f"{idx}. **{citation.title}** ({citation.score:.2f})")
            lines.append(f"   URL: {citation.source_url}")
            if citation.snippet:
                lines.append(f"   Snippet: {citation.snippet[:150]}...")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_citations_dict(self) -> Dict[int, Dict]:
        """
        Return citations as dictionary for API responses.
        
        Returns:
            Dict mapping indices to citation metadata
        """
        sorted_citations = sorted(
            self.citations.values(),
            key=lambda c: c.score,
            reverse=True
        )
        
        result = {}
        for idx, citation in enumerate(sorted_citations, 1):
            result[idx] = {
                "title": citation.title,
                "url": citation.source_url,
                "score": float(citation.score),
                "type": citation.citation_type,
                "snippet": citation.snippet,
                "image_name": citation.image_name
            }
        
        return result
    
    def clear(self) -> None:
        """Clear all citations."""
        self.citations.clear()
        self._counter = 1
    
    def count(self) -> int:
        """Return number of unique citations."""
        return len(self.citations)
    
    def get_all(self) -> List[Citation]:
        """Return all citations sorted by score."""
        return sorted(
            self.citations.values(),
            key=lambda c: c.score,
            reverse=True
        )
