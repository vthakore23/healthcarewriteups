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
            try:
                # Try newer client initialization first
                self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            except (TypeError, AttributeError):
                # Fall back to setting API key globally for older versions
                self.client = openai
        elif self.ai_provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        else:
            raise ValueError("No valid AI API key found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    def _determine_ai_provider(self):
        """Determine which AI provider to use based on available API keys"""
        # Debug: Print what we actually have
        logger.info(f"Checking API keys - Anthropic: {'Yes' if config.ANTHROPIC_API_KEY else 'No'}, OpenAI: {'Yes' if config.OPENAI_API_KEY else 'No'}")
        logger.info(f"AI Model configured: {config.AI_MODEL}")
        
        if config.ANTHROPIC_API_KEY and 'claude' in config.AI_MODEL.lower():
            logger.info("Using Anthropic Claude")
            return 'anthropic'
        elif config.OPENAI_API_KEY and ('gpt' in config.AI_MODEL.lower() or not config.ANTHROPIC_API_KEY):
            logger.info("Using OpenAI GPT")
            return 'openai'
        elif config.ANTHROPIC_API_KEY:
            logger.info("Using Anthropic Claude (fallback)")
            return 'anthropic'
        
        logger.error(f"No valid API key found. Anthropic: {bool(config.ANTHROPIC_API_KEY)}, OpenAI: {bool(config.OPENAI_API_KEY)}")
        return None
    
    def generate_summary(self, article):
        """Generate a structured summary for an article matching investment analysis requirements"""
        prompt = config.SUMMARY_PROMPT.format(article_text=article.content[:8000])  # Limit content length
        
        try:
            if self.ai_provider == 'openai':
                try:
                    # Try new client style
                    response = self.client.chat.completions.create(
                        model=config.AI_MODEL,
                        messages=[
                            {"role": "system", "content": "You are creating structured healthcare news summaries for investment professionals using the exact required format."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.3
                    )
                    summary_text = response.choices[0].message.content
                except AttributeError:
                    # Fall back to module-level API calls
                    response = openai.ChatCompletion.create(
                        model=config.AI_MODEL,
                        messages=[
                            {"role": "system", "content": "You are creating structured healthcare news summaries for investment professionals using the exact required format."},
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
                    system="You are creating structured healthcare news summaries for investment professionals using the exact required format."
                )
                summary_text = response.content[0].text
            
            # Validate summary against Chris's requirements
            word_count = len(summary_text.split())
            if word_count < config.MIN_WORD_COUNT:
                logger.warning(f"Summary too short ({word_count} words), regenerating...")
                return self._regenerate_with_more_detail(article, summary_text)
            
            # Validate structure
            required_sections = ["Company Name:", "News Event:", "News Summary:", "Standout Points:", "Additional Developments:"]
            missing_sections = [section for section in required_sections if section not in summary_text]
            if missing_sections:
                logger.warning(f"Missing sections: {missing_sections}, regenerating...")
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
        """Regenerate summary with Chris's exact requirements"""
        followup_prompt = f"""
        The following summary doesn't meet Chris's exact requirements. Please reformat it to match his EXACT structure:
        
        REQUIRED STRUCTURE (approximately 600 words total):
        
        Company Name: [Insert Company Name with ticker if available]
        
        News Event: [Insert Type: Earnings, Data Release, Conference, Partnership, Leadership Change, etc.]
        
        News Summary:
        [Provide a concise paragraph (5 sentences) summarizing the key news, including critical figures, events, and implications.]
        
        Standout Points:
        [THIS MUST BE THE "MEATIEST" SECTION with ALL quantifiable data including exact percentages, patient numbers, financial figures, dosing, timelines, safety data, mechanism explanations, and market differentiation factors.]
        
        Additional Developments:
        [Insert info on partnerships, acquisitions, collaborations, or strategic initiatives tied to the news.]
        
        CRITICAL: Make "Standout Points" the most detailed section with all quantifiable data. Be very specific about mechanisms, drugs, targets, and why things are different.
        
        Current summary to improve:
        {initial_summary}
        
        Original article for reference:
        {article.content[:8000]}
        
        Ensure the summary is approximately 600 words with "Standout Points" being the longest, most detailed section.
        """
        
        try:
            if self.ai_provider == 'openai':
                try:
                    # Try new client style
                    response = self.client.chat.completions.create(
                        model=config.AI_MODEL,
                        messages=[
                            {"role": "system", "content": "You are creating healthcare summaries for Chris at Opaley Management. Follow his exact format and make 'Standout Points' the meatiest section."},
                            {"role": "user", "content": followup_prompt}
                        ],
                        max_tokens=1200,
                        temperature=0.3
                    )
                    return response.choices[0].message.content
                except AttributeError:
                    # Fall back to module-level API calls
                    response = openai.ChatCompletion.create(
                        model=config.AI_MODEL,
                        messages=[
                            {"role": "system", "content": "You are creating healthcare summaries for Chris at Opaley Management. Follow his exact format and make 'Standout Points' the meatiest section."},
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
                    system="You are creating healthcare summaries for Chris at Opaley Management. Follow his exact format and make 'Standout Points' the meatiest section."
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
    
    def generate_analysis(self, summary_text, article_title="", company_name=""):
        """Generate analysis focused on why this news is interesting and its implications (Chris's requirements)"""
        
        # Extract company name from summary if not provided
        if not company_name:
            company_name = self._extract_company_name(summary_text)
        
        # Create analysis prompt matching Chris's requirements
        prompt = config.ANALYSIS_PROMPT.format(
            summary=summary_text,
            article_title=article_title,
            company_name=company_name
        )
        
        # Add Chris's specific requirements
        prompt += f"""

CRITICAL REQUIREMENTS FOR CHRIS'S ANALYSIS:
- Focus on WHY this event is interesting and worth attention
- Discuss longer-term implications for the company (good, bad, or indifferent)
- Include additional research and insights beyond the press release
- CITE SOURCES for any external research or data not from the original article
- Use phrases like "According to industry data..." or "Market research shows..."
- Include direct quotes and figures when relevant
- Provide specific, quantifiable insights where possible
- Target 400-600 words of additional analysis

STRUCTURE YOUR RESPONSE AS:
1. Why This Event is Interesting
2. Potential Implications (longer term)  
3. Additional Research & Insights (with proper source citations)
"""
        
        try:
            system_message = f"""You are providing additional analysis for Chris and Jim at Opaley Management. They want to understand:

1. WHY this healthcare/biotech news event is interesting and noteworthy
2. What the IMPLICATIONS are for the company (thinking longer term)
3. ADDITIONAL RESEARCH and insights beyond the press release

CRITICAL: When you reference any data or information not from the original press release, you MUST cite the source clearly. Use phrases like:
- "According to [source]..."
- "Industry data from [source] shows..."
- "Market research indicates..."

Be specific about what makes this news stand out and why investors should pay attention."""

            if self.ai_provider == 'openai':
                try:
                    # Try new client style
                    response = self.client.chat.completions.create(
                        model=config.AI_MODEL,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1200,
                        temperature=0.3
                    )
                    return response.choices[0].message.content
                except AttributeError:
                    # Fall back to module-level API calls
                    response = openai.ChatCompletion.create(
                        model=config.AI_MODEL,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1200,
                        temperature=0.3
                    )
                    return response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.client.messages.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1200,
                    temperature=0.3,
                    system=system_message
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
                try:
                    # Try new client style
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
                except AttributeError:
                    # Fall back to module-level API calls
                    response = openai.ChatCompletion.create(
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