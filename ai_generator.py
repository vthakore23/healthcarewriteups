"""
AI-powered summary generator for healthcare news
"""
import openai
import anthropic
import logging
import re
from typing import List, Dict, Tuple
import config

logger = logging.getLogger(__name__)


class AISummaryGenerator:
    """Generate summaries using AI (OpenAI or Anthropic)"""
    
    def __init__(self):
        self.ai_provider = self._determine_ai_provider()
        
        if self.ai_provider == 'openai':
            openai.api_key = config.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        elif self.ai_provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        else:
            raise ValueError("No valid AI API key found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    def _determine_ai_provider(self):
        """Determine which AI provider to use based on available API keys"""
        if config.ANTHROPIC_API_KEY and 'claude' in config.AI_MODEL.lower():
            return 'anthropic'
        elif config.OPENAI_API_KEY:
            return 'openai'
        elif config.ANTHROPIC_API_KEY:
            return 'anthropic'
        return None
    
    def generate_summary(self, article):
        """Generate a structured summary for an article"""
        prompt = config.SUMMARY_PROMPT.format(article_text=article.content[:8000])  # Limit content length
        
        try:
            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert healthcare and biotech analyst creating structured summaries for investors."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                summary_text = response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.client.messages.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3,
                    system="You are an expert healthcare and biotech analyst creating structured summaries for investors."
                )
                summary_text = response.content[0].text
            
            # Ensure summary meets word count requirements
            word_count = len(summary_text.split())
            if word_count < config.MIN_WORD_COUNT:
                logger.warning(f"Summary too short ({word_count} words), regenerating...")
                return self._regenerate_with_more_detail(article, summary_text)
            
            # Extract company name from summary
            company_name = self._extract_company_name(summary_text)
            if company_name:
                article.company_name = company_name
            
            return summary_text
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def _regenerate_with_more_detail(self, article, initial_summary):
        """Regenerate summary with more detail if too short"""
        followup_prompt = f"""
        The following summary is too brief. Please expand it to approximately 600 words while maintaining the same structure:
        
        {initial_summary}
        
        Original article for reference:
        {article.content[:8000]}
        
        Please add more specific details about:
        - Quantitative data and metrics
        - Scientific mechanisms and differentiation
        - Market implications
        - Competitive positioning
        """
        
        try:
            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert healthcare and biotech analyst."},
                        {"role": "user", "content": followup_prompt}
                    ],
                    max_tokens=1200,
                    temperature=0.3
                )
                return response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.client.messages.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "user", "content": followup_prompt}
                    ],
                    max_tokens=1200,
                    temperature=0.3,
                    system="You are an expert healthcare and biotech analyst."
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error regenerating summary: {e}")
            return initial_summary
    
    def _extract_company_name(self, summary_text):
        """Extract company name from summary"""
        # Look for "Company Name: " pattern
        match = re.search(r'Company Name:\s*([^\n]+)', summary_text)
        if match:
            return match.group(1).strip()
        return None
    
    def generate_analysis(self, summary_text):
        """Generate additional analysis for interesting articles"""
        prompt = config.ANALYSIS_PROMPT.format(summary=summary_text)
        
        try:
            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a senior healthcare investment analyst providing strategic insights."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.4
                )
                return response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.client.messages.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.4,
                    system="You are a senior healthcare investment analyst providing strategic insights."
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return None
    
    def select_interesting_articles(self, summaries: List[Dict]) -> List[int]:
        """Use AI to select the most interesting articles"""
        if len(summaries) <= 2:
            return list(range(len(summaries)))
        
        summaries_text = "\n\n---\n\n".join([
            f"Article {i+1}: {s['title']}\n{s['summary'][:500]}..."
            for i, s in enumerate(summaries)
        ])
        
        prompt = f"""
        Review the following healthcare news summaries and select the 1-2 most interesting and significant articles for investors.
        
        Consider:
        - Market impact potential
        - Scientific breakthrough significance
        - Financial implications
        - Strategic importance
        - Novelty of the development
        
        {summaries_text}
        
        Return ONLY the article numbers (e.g., "1, 3") of the most interesting articles. No explanation needed.
        """
        
        try:
            if self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert healthcare investor."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=50,
                    temperature=0.2
                )
                selection_text = response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.client.messages.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=50,
                    temperature=0.2,
                    system="You are an expert healthcare investor."
                )
                selection_text = response.content[0].text
            
            # Parse the selection
            numbers = re.findall(r'\d+', selection_text)
            selected = [int(n) - 1 for n in numbers if 0 < int(n) <= len(summaries)]
            
            return selected[:2]  # Maximum 2 articles
            
        except Exception as e:
            logger.error(f"Error selecting articles: {e}")
            # Default to first two articles
            return [0, 1] if len(summaries) > 1 else [0] 