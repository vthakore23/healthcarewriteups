#!/usr/bin/env python3
"""
Demo script to create a sample healthcare news analysis with enhanced features
"""
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from scraper_optimized import NewsArticle
from ai_generator_optimized import OptimizedAISummaryGenerator
from email_sender import EmailSender
import config

def create_demo_articles():
    """Create mock articles for demonstration"""
    now = datetime.now()
    
    articles = [
        NewsArticle(
            title="Neurocrine Biosciences Presents New Data Showing Significant Reduction in Chorea for Huntington's Disease Patients",
            url="https://lifesciencereport.com/news/neurocrine-huntingtons-data-2024",
            content="""
            Neurocrine Biosciences, Inc. (NASDAQ: NBIX) today announced positive results from a Phase 3 clinical trial of INGREZZA® (valbenazine) in patients with chorea associated with Huntington's disease (HD). 
            
            The KINECT®-HD study met its primary endpoint, demonstrating a statistically significant reduction in chorea severity compared to placebo. In the 12-week double-blind treatment period, patients receiving INGREZZA showed a 4.4-point improvement on the Unified Huntington's Disease Rating Scale Total Motor Score (UHDRS-TMS) chorea subscore compared to a 1.9-point improvement with placebo (treatment difference: -2.5 points; 95% CI: -3.5, -1.4; p<0.001).
            
            The study enrolled 128 patients with HD chorea across multiple international sites. The most common adverse events in the INGREZZA group were somnolence (13.1%), fatigue (8.2%), and depression (6.6%). The safety profile was consistent with previous studies of INGREZZA.
            
            "These results represent a significant advancement for HD patients who have limited treatment options," said Dr. Kevin Biglan, Chief Medical Officer at Neurocrine Biosciences. "INGREZZA has already demonstrated its efficacy in tardive dyskinesia, and these data suggest it could provide meaningful benefit for HD chorea as well."
            
            Neurocrine plans to submit these data to regulatory authorities in Q1 2025 for potential label expansion. The company is also exploring additional movement disorder indications for INGREZZA as part of its broader neurological portfolio strategy.
            """,
            published_date=now,
            company_name="Neurocrine Biosciences, Inc."
        ),
        
        NewsArticle(
            title="BioMarin Pharmaceutical Reports Breakthrough Gene Therapy Results for Hemophilia A",
            url="https://lifesciencereport.com/news/biomarin-hemophilia-gene-therapy-2024",
            content="""
            BioMarin Pharmaceutical Inc. (NASDAQ: BMRN) announced compelling Phase 3 results for its investigational gene therapy BMN 270 (valoctocogene roxaparvovec) for severe hemophilia A. The GENEr8-1 study demonstrated sustained factor VIII activity levels and significant reduction in bleeding episodes.
            
            In the study of 134 participants, BMN 270 showed factor VIII activity levels of 42.5 IU/dL at 52 weeks post-infusion, representing normal to near-normal levels. Participants experienced a 96.7% reduction in treated bleeding episodes compared to their pre-study prophylaxis regimen. The annual bleeding rate decreased from 16.8 episodes to 0.6 episodes per year.
            
            The gene therapy uses an adeno-associated virus (AAV) vector to deliver a functional copy of the factor VIII gene directly to liver cells. Unlike traditional factor replacement therapy that requires frequent infusions, BMN 270 is designed to provide sustained factor VIII production with a single treatment.
            
            "These results exceed our expectations and represent a potential paradigm shift in hemophilia A treatment," said BioMarin CEO Jean-Jacques Bienaime. "The durability of response and the dramatic reduction in bleeding episodes could transform patients' lives."
            
            The most common adverse events were mild to moderate and included headache (29%), nausea (22%), and fatigue (19%). No serious adverse events were attributed to the gene therapy.
            
            BioMarin plans to submit a Biologics License Application (BLA) to the FDA in Q2 2025. The therapy has received Fast Track designation and Breakthrough Therapy designation from the FDA.
            """,
            published_date=now,
            company_name="BioMarin Pharmaceutical Inc."
        ),
        
        NewsArticle(
            title="Moderna Announces Strategic Partnership with NIH for Next-Generation Vaccine Platform",
            url="https://lifesciencereport.com/news/moderna-nih-partnership-2024",
            content="""
            Moderna, Inc. (NASDAQ: MRNA) today announced a five-year strategic research collaboration with the National Institutes of Health (NIH) to develop next-generation vaccine technologies using self-amplifying RNA (saRNA) platforms.
            
            The partnership will focus on developing vaccines for pandemic preparedness, with initial targets including influenza, respiratory syncytial virus (RSV), and emerging infectious diseases. The collaboration combines Moderna's mRNA technology expertise with NIH's extensive research capabilities and biosafety infrastructure.
            
            Under the agreement, Moderna will receive up to $200 million in funding over five years, with potential for additional milestone payments. The company will contribute its proprietary saRNA technology, manufacturing capabilities, and clinical development expertise.
            
            "This partnership leverages the proven success of mRNA vaccines while advancing next-generation technologies that could provide even greater protection and durability," said Dr. Stephen Hoge, President of Moderna. "Self-amplifying RNA has the potential to deliver improved immune responses at lower doses."
            
            The saRNA platform differs from traditional mRNA by including genes that enable the RNA to replicate within cells, potentially leading to stronger and longer-lasting immune responses. This could allow for smaller doses and potentially fewer vaccinations.
            
            Moderna's stock has gained 23% since announcing preliminary saRNA data in November. The company expects to begin Phase 1 trials for the first saRNA vaccine candidates in late 2025.
            
            The partnership also includes provisions for technology transfer to support global vaccine manufacturing and distribution in low- and middle-income countries.
            """,
            published_date=now,
            company_name="Moderna, Inc."
        )
    ]
    
    return articles

def run_demo_analysis():
    """Run analysis with demo articles"""
    print("🔬 GENERATING DEMO HEALTHCARE NEWS ANALYSIS")
    print("=" * 60)
    
    # Create demo articles
    print("\n📋 Creating demo articles...")
    articles = create_demo_articles()
    print(f"✅ Created {len(articles)} demo articles")
    
    # Initialize AI generator
    print("\n🤖 Initializing AI generator...")
    ai_generator = OptimizedAISummaryGenerator(max_workers=1)
    print(f"✅ AI generator ready (using {ai_generator.ai_provider})")
    
    # Generate summaries
    print("\n📊 Generating summaries...")
    summaries = []
    for i, article in enumerate(articles):
        print(f"   Processing article {i+1}/{len(articles)}: {article.title[:50]}...")
        summary_text = ai_generator.generate_summary(article)
        if summary_text:
            summaries.append({
                'title': article.title,
                'url': article.url,
                'summary': summary_text,
                'company_name': article.company_name,
                'article': article
            })
            print(f"   ✅ Summary generated")
        else:
            print(f"   ❌ Summary failed")
    
    print(f"\n✅ Generated {len(summaries)} summaries")
    
    # Select interesting articles
    print("\n🎯 Selecting most interesting articles...")
    interesting_indices = ai_generator.select_interesting_articles_smart(summaries)
    print(f"✅ Selected {len(interesting_indices)} articles for deep analysis")
    
    # Generate enhanced analysis
    print("\n🔍 Generating enhanced news-specific analysis...")
    analyses = []
    for i, idx in enumerate(interesting_indices):
        if idx < len(summaries):
            article_title = summaries[idx]['title']
            company_name = summaries[idx].get('company_name', '')
            print(f"   📊 Analyzing {i+1}/{len(interesting_indices)}: {company_name}")
            
            analysis_text = ai_generator.generate_analysis(
                summary_text=summaries[idx]['summary'],
                article_title=article_title,
                company_name=company_name
            )
            
            if analysis_text:
                analyses.append({
                    'title': article_title,
                    'url': summaries[idx]['url'],
                    'summary': summaries[idx]['summary'],
                    'analysis': analysis_text,
                    'company_name': company_name
                })
                print(f"   ✅ News-specific analysis complete")
    
    # Save reports
    print("\n💾 Saving reports...")
    
    # Save HTML report
    date_str = datetime.now().strftime('%Y-%m-%d')
    html_file = os.path.join(config.REPORTS_DIR, f'demo_report_{date_str}.html')
    
    email_sender = EmailSender()
    html_content = email_sender._generate_html_content(summaries, analyses, datetime.now())
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Demo report saved: {html_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 DEMO ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"📄 Report: {html_file}")
    print(f"📊 Articles processed: {len(articles)}")
    print(f"📝 Summaries generated: {len(summaries)}")
    print(f"🔍 Deep analyses: {len(analyses)}")
    print("\n💡 Features demonstrated:")
    print("   ✅ News-specific analysis (not generic company info)")
    print("   ✅ Enhanced prompts with investment focus")
    print("   ✅ Company-specific insights")
    print("   ✅ Beautiful HTML report formatting")
    print("   ✅ Prominent article titles and company names")

if __name__ == "__main__":
    run_demo_analysis() 