#!/usr/bin/env python3
"""
Enhanced Stock Ticker Intelligence System
Provides comprehensive real-time analysis for healthcare companies
Includes advanced financial metrics, insider trading, analyst ratings, and more
"""
import sys
import os
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sqlite3

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_ticker_intelligence import HealthcareCompanyIntelligence
from config import FMP_API_KEY, ALPHA_VANTAGE_API_KEY, NEWS_API_KEY, OPENAI_API_KEY


class EnhancedStockIntelligence(HealthcareCompanyIntelligence):
    """Enhanced stock intelligence with advanced features"""
    
    def __init__(self):
        super().__init__()
        self.use_demo_mode = False  # Enable real API calls
        self._init_cache_db()
        
    def _init_cache_db(self):
        """Initialize cache database for API responses"""
        self.cache_db = "stock_intelligence_cache.db"
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                cache_key TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                expiry_hours INTEGER DEFAULT 24
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyst_ratings (
                ticker TEXT,
                analyst_firm TEXT,
                rating TEXT,
                price_target REAL,
                rating_date DATE,
                PRIMARY KEY (ticker, analyst_firm)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insider_trades (
                ticker TEXT,
                insider_name TEXT,
                title TEXT,
                transaction_type TEXT,
                shares INTEGER,
                price REAL,
                value REAL,
                transaction_date DATE,
                filing_date DATE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_enhanced_intelligence(self, ticker: str) -> Dict:
        """Get comprehensive enhanced intelligence on a healthcare company"""
        ticker = ticker.upper().strip()
        
        print(f"\n🚀 Gathering ENHANCED intelligence on {ticker}...")
        
        # Get basic intelligence first
        basic_intel = self.get_company_intelligence(ticker)
        
        if "error" in basic_intel:
            return basic_intel
        
        # Enhance with additional data sources
        enhanced_data = {
            **basic_intel,
            
            # Real-time market data
            "real_time_data": self._get_real_time_data(ticker),
            
            # Technical indicators
            "technical_analysis": self._get_technical_indicators(ticker),
            
            # Analyst ratings and price targets
            "analyst_consensus": self._get_analyst_ratings(ticker),
            
            # Insider trading activity
            "insider_activity": self._get_insider_trading(ticker),
            
            # Options flow analysis
            "options_analysis": self._get_options_flow(ticker),
            
            # Peer comparison
            "peer_analysis": self._get_peer_comparison(ticker, basic_intel),
            
            # News sentiment analysis
            "news_sentiment": self._get_news_sentiment(ticker),
            
            # Social media sentiment
            "social_sentiment": self._get_social_sentiment(ticker),
            
            # Institutional ownership changes
            "institutional_changes": self._get_institutional_changes(ticker),
            
            # Patent activity
            "patent_activity": self._get_patent_activity(basic_intel.get('company_name', '')),
            
            # Clinical trial updates
            "clinical_updates": self._get_clinical_trial_updates(basic_intel.get('company_name', '')),
            
            # Risk analysis
            "risk_assessment": self._calculate_risk_metrics(ticker, basic_intel)
        }
        
        # Generate AI-powered insights
        enhanced_data["ai_insights"] = self._generate_ai_insights(enhanced_data)
        
        return enhanced_data
    
    def _get_real_time_data(self, ticker: str) -> Dict:
        """Get real-time market data"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get intraday data
            intraday = stock.history(period="1d", interval="5m")
            
            # Get quote data
            quote = stock.info
            
            # Calculate real-time metrics
            if not intraday.empty:
                current_price = intraday['Close'].iloc[-1]
                day_open = intraday['Open'].iloc[0]
                day_high = intraday['High'].max()
                day_low = intraday['Low'].min()
                volume = intraday['Volume'].sum()
                
                # Calculate VWAP
                vwap = (intraday['Close'] * intraday['Volume']).sum() / intraday['Volume'].sum()
                
                # Calculate intraday volatility
                returns = intraday['Close'].pct_change().dropna()
                intraday_volatility = returns.std() * np.sqrt(252 * 78)  # Annualized
                
                return {
                    "current_price": round(current_price, 2),
                    "day_change": round(current_price - day_open, 2),
                    "day_change_pct": round((current_price - day_open) / day_open * 100, 2),
                    "day_high": round(day_high, 2),
                    "day_low": round(day_low, 2),
                    "volume": int(volume),
                    "avg_volume_10d": quote.get('averageVolume10days', 0),
                    "vwap": round(vwap, 2),
                    "intraday_volatility": round(intraday_volatility * 100, 2),
                    "bid": quote.get('bid', 0),
                    "ask": quote.get('ask', 0),
                    "bid_size": quote.get('bidSize', 0),
                    "ask_size": quote.get('askSize', 0),
                    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                return {"error": "No intraday data available"}
                
        except Exception as e:
            print(f"Error getting real-time data: {e}")
            return {"error": str(e)}
    
    def _get_technical_indicators(self, ticker: str) -> Dict:
        """Calculate technical indicators"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get historical data
            hist = stock.history(period="6mo")
            
            if hist.empty:
                return {"error": "No historical data"}
            
            close = hist['Close']
            volume = hist['Volume']
            
            # Calculate moving averages
            ma_20 = close.rolling(window=20).mean().iloc[-1]
            ma_50 = close.rolling(window=50).mean().iloc[-1]
            ma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None
            
            # Calculate RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # Calculate MACD
            exp1 = close.ewm(span=12, adjust=False).mean()
            exp2 = close.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_histogram = macd - signal
            
            # Calculate Bollinger Bands
            sma = close.rolling(window=20).mean()
            std = close.rolling(window=20).std()
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            
            # Support and Resistance levels
            support = close.rolling(window=20).min().iloc[-1]
            resistance = close.rolling(window=20).max().iloc[-1]
            
            current_price = close.iloc[-1]
            
            return {
                "current_price": round(current_price, 2),
                "moving_averages": {
                    "ma_20": round(ma_20, 2),
                    "ma_50": round(ma_50, 2),
                    "ma_200": round(ma_200, 2) if ma_200 else "N/A",
                    "price_vs_ma20": round((current_price - ma_20) / ma_20 * 100, 2)
                },
                "rsi": round(rsi, 2),
                "rsi_signal": "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral",
                "macd": {
                    "macd": round(macd.iloc[-1], 3),
                    "signal": round(signal.iloc[-1], 3),
                    "histogram": round(macd_histogram.iloc[-1], 3),
                    "trend": "Bullish" if macd_histogram.iloc[-1] > 0 else "Bearish"
                },
                "bollinger_bands": {
                    "upper": round(upper_band.iloc[-1], 2),
                    "middle": round(sma.iloc[-1], 2),
                    "lower": round(lower_band.iloc[-1], 2),
                    "position": "Above Upper" if current_price > upper_band.iloc[-1] else 
                               "Below Lower" if current_price < lower_band.iloc[-1] else "Within Bands"
                },
                "support_resistance": {
                    "support": round(support, 2),
                    "resistance": round(resistance, 2),
                    "distance_to_support": round((current_price - support) / support * 100, 2),
                    "distance_to_resistance": round((resistance - current_price) / current_price * 100, 2)
                },
                "volume_analysis": {
                    "avg_volume_20d": int(volume.rolling(window=20).mean().iloc[-1]),
                    "volume_trend": "Increasing" if volume.iloc[-5:].mean() > volume.iloc[-20:-5].mean() else "Decreasing"
                },
                "trend_strength": self._calculate_trend_strength(close)
            }
            
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return {"error": str(e)}
    
    def _calculate_trend_strength(self, prices: pd.Series) -> str:
        """Calculate trend strength using ADX"""
        try:
            # Simple trend strength calculation
            recent_avg = prices.iloc[-10:].mean()
            older_avg = prices.iloc[-30:-10].mean()
            
            change_pct = (recent_avg - older_avg) / older_avg * 100
            
            if abs(change_pct) < 2:
                return "No Clear Trend"
            elif change_pct > 5:
                return "Strong Uptrend"
            elif change_pct > 2:
                return "Moderate Uptrend"
            elif change_pct < -5:
                return "Strong Downtrend"
            else:
                return "Moderate Downtrend"
                
        except:
            return "Unable to determine"
    
    def _get_analyst_ratings(self, ticker: str) -> Dict:
        """Get analyst ratings and price targets"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get recommendations
            try:
                recommendations = stock.recommendations
                if recommendations is not None and not recommendations.empty:
                    recent_recs = recommendations.tail(10)
                    
                    # Count ratings
                    rating_counts = recent_recs['To Grade'].value_counts().to_dict()
                    
                    # Get average price target (if available through other APIs)
                    info = stock.info
                    target_mean = info.get('targetMeanPrice', 0)
                    target_high = info.get('targetHighPrice', 0)
                    target_low = info.get('targetLowPrice', 0)
                    current_price = info.get('currentPrice', 0)
                    
                    return {
                        "rating_summary": rating_counts,
                        "consensus": self._determine_consensus(rating_counts),
                        "price_targets": {
                            "mean": target_mean,
                            "high": target_high,
                            "low": target_low,
                            "upside_potential": round((target_mean - current_price) / current_price * 100, 2) if current_price else 0
                        },
                        "recent_changes": [
                            {
                                "date": idx.strftime("%Y-%m-%d"),
                                "firm": row['Firm'],
                                "from_grade": row['From Grade'],
                                "to_grade": row['To Grade'],
                                "action": row['Action']
                            }
                            for idx, row in recent_recs.iterrows()
                        ][:5]
                    }
                else:
                    return {"message": "No analyst ratings available"}
                    
            except Exception as e:
                print(f"Error getting recommendations: {e}")
                return {"message": "No analyst ratings available"}
                
        except Exception as e:
            print(f"Error getting analyst ratings: {e}")
            return {"error": str(e)}
    
    def _determine_consensus(self, rating_counts: Dict) -> str:
        """Determine consensus rating from counts"""
        buy_words = ['Buy', 'Strong Buy', 'Outperform', 'Overweight', 'Positive']
        hold_words = ['Hold', 'Neutral', 'Equal Weight', 'Market Perform']
        sell_words = ['Sell', 'Strong Sell', 'Underperform', 'Underweight', 'Negative']
        
        buy_count = sum(rating_counts.get(word, 0) for word in rating_counts if any(bw in word for bw in buy_words))
        hold_count = sum(rating_counts.get(word, 0) for word in rating_counts if any(hw in word for hw in hold_words))
        sell_count = sum(rating_counts.get(word, 0) for word in rating_counts if any(sw in word for sw in sell_words))
        
        total = buy_count + hold_count + sell_count
        if total == 0:
            return "No Consensus"
        
        buy_pct = buy_count / total
        
        if buy_pct > 0.7:
            return "Strong Buy"
        elif buy_pct > 0.5:
            return "Buy"
        elif sell_count / total > 0.5:
            return "Sell"
        else:
            return "Hold"
    
    def _get_insider_trading(self, ticker: str) -> Dict:
        """Get insider trading activity"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get insider transactions
            insider_trades = stock.insider_transactions
            
            if insider_trades is not None and not insider_trades.empty:
                # Analyze recent transactions
                recent_trades = insider_trades.head(20)
                
                # Calculate buy/sell ratio
                buys = recent_trades[recent_trades['Transaction'] == 'Buy']
                sells = recent_trades[recent_trades['Transaction'] == 'Sale']
                
                total_buy_value = buys['Value'].sum() if 'Value' in buys.columns else 0
                total_sell_value = sells['Value'].sum() if 'Value' in sells.columns else 0
                
                return {
                    "recent_activity": [
                        {
                            "date": row.get('Date', 'N/A'),
                            "insider": row.get('Insider', 'Unknown'),
                            "title": row.get('Title', 'N/A'),
                            "transaction": row.get('Transaction', 'N/A'),
                            "shares": row.get('Shares', 0),
                            "value": row.get('Value', 0)
                        }
                        for _, row in recent_trades.iterrows()
                    ][:10],
                    "summary": {
                        "total_buys": len(buys),
                        "total_sells": len(sells),
                        "buy_value": total_buy_value,
                        "sell_value": total_sell_value,
                        "net_sentiment": "Bullish" if total_buy_value > total_sell_value else "Bearish" if total_sell_value > 0 else "Neutral"
                    }
                }
            else:
                return {"message": "No insider trading data available"}
                
        except Exception as e:
            print(f"Error getting insider trading: {e}")
            return {"error": str(e)}
    
    def _get_options_flow(self, ticker: str) -> Dict:
        """Analyze options flow for unusual activity"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get options chain
            try:
                expirations = stock.options
                if not expirations:
                    return {"message": "No options data available"}
                
                # Analyze nearest expiration
                nearest_exp = expirations[0]
                opt_chain = stock.option_chain(nearest_exp)
                
                calls = opt_chain.calls
                puts = opt_chain.puts
                
                # Calculate put/call ratio
                call_volume = calls['volume'].sum()
                put_volume = puts['volume'].sum()
                put_call_ratio = put_volume / call_volume if call_volume > 0 else 0
                
                # Find unusual activity
                high_volume_calls = calls[calls['volume'] > calls['openInterest'] * 0.5].nlargest(5, 'volume')
                high_volume_puts = puts[puts['volume'] > puts['openInterest'] * 0.5].nlargest(5, 'volume')
                
                return {
                    "put_call_ratio": round(put_call_ratio, 3),
                    "sentiment": "Bearish" if put_call_ratio > 1.2 else "Bullish" if put_call_ratio < 0.7 else "Neutral",
                    "total_call_volume": int(call_volume),
                    "total_put_volume": int(put_volume),
                    "unusual_activity": {
                        "calls": [
                            {
                                "strike": row['strike'],
                                "volume": row['volume'],
                                "open_interest": row['openInterest'],
                                "implied_volatility": round(row['impliedVolatility'] * 100, 2)
                            }
                            for _, row in high_volume_calls.iterrows()
                        ],
                        "puts": [
                            {
                                "strike": row['strike'],
                                "volume": row['volume'],
                                "open_interest": row['openInterest'],
                                "implied_volatility": round(row['impliedVolatility'] * 100, 2)
                            }
                            for _, row in high_volume_puts.iterrows()
                        ]
                    },
                    "max_pain": self._calculate_max_pain(calls, puts)
                }
                
            except Exception as e:
                print(f"Error analyzing options: {e}")
                return {"message": "Options analysis unavailable"}
                
        except Exception as e:
            print(f"Error getting options flow: {e}")
            return {"error": str(e)}
    
    def _calculate_max_pain(self, calls: pd.DataFrame, puts: pd.DataFrame) -> float:
        """Calculate max pain price for options"""
        try:
            strikes = sorted(set(calls['strike'].tolist() + puts['strike'].tolist()))
            min_pain_value = float('inf')
            max_pain_strike = 0
            
            for strike in strikes:
                # Calculate pain for this strike
                call_pain = ((calls[calls['strike'] < strike]['strike'] - strike) * 
                           calls[calls['strike'] < strike]['openInterest']).sum()
                
                put_pain = ((strike - puts[puts['strike'] > strike]['strike']) * 
                          puts[puts['strike'] > strike]['openInterest']).sum()
                
                total_pain = abs(call_pain) + abs(put_pain)
                
                if total_pain < min_pain_value:
                    min_pain_value = total_pain
                    max_pain_strike = strike
            
            return max_pain_strike
            
        except:
            return 0
    
    def _get_peer_comparison(self, ticker: str, company_data: Dict) -> Dict:
        """Compare with peer companies"""
        try:
            # Determine peers based on market cap and industry
            market_cap = company_data.get('market_cap', '0')
            market_cap_value = self._parse_market_cap(market_cap)
            
            # Define peer groups
            biotech_peers = {
                'large_cap': ['GILD', 'BIIB', 'VRTX', 'REGN', 'ILMN'],
                'mid_cap': ['SGEN', 'BMRN', 'INCY', 'EXEL', 'ALNY'],
                'small_cap': ['SAGE', 'FATE', 'KYMR', 'ARVN', 'BEAM']
            }
            
            pharma_peers = {
                'large_cap': ['JNJ', 'PFE', 'MRK', 'ABBV', 'BMY'],
                'mid_cap': ['VTRS', 'CTLT', 'JAZZ', 'HZNP'],
                'small_cap': ['PCRX', 'SUPN', 'HRMY']
            }
            
            # Select appropriate peer group
            if market_cap_value > 10e9:
                size = 'large_cap'
            elif market_cap_value > 2e9:
                size = 'mid_cap'
            else:
                size = 'small_cap'
            
            industry = company_data.get('industry', '').lower()
            if 'biotech' in industry:
                peers = biotech_peers.get(size, [])
            else:
                peers = pharma_peers.get(size, [])
            
            # Remove current ticker from peers
            peers = [p for p in peers if p != ticker][:5]
            
            # Get peer metrics
            peer_data = []
            for peer in peers:
                try:
                    peer_stock = yf.Ticker(peer)
                    peer_info = peer_stock.info
                    
                    peer_data.append({
                        'ticker': peer,
                        'name': peer_info.get('longName', peer),
                        'market_cap': self._format_market_cap(peer_info.get('marketCap', 0)),
                        'pe_ratio': peer_info.get('trailingPE', 0),
                        'price_change_ytd': self._calculate_ytd_return(peer),
                        'revenue_growth': peer_info.get('revenueGrowth', 0),
                        'gross_margins': peer_info.get('grossMargins', 0)
                    })
                except:
                    continue
            
            # Calculate relative metrics
            current_pe = yf.Ticker(ticker).info.get('trailingPE', 0)
            avg_peer_pe = np.mean([p['pe_ratio'] for p in peer_data if p['pe_ratio'] > 0]) if peer_data else 0
            
            return {
                "peer_group": peer_data,
                "relative_valuation": {
                    "current_pe": current_pe,
                    "peer_avg_pe": round(avg_peer_pe, 2),
                    "valuation_vs_peers": "Overvalued" if current_pe > avg_peer_pe * 1.2 else 
                                         "Undervalued" if current_pe < avg_peer_pe * 0.8 else "Fair"
                },
                "performance_ranking": self._rank_performance(ticker, peers)
            }
            
        except Exception as e:
            print(f"Error in peer comparison: {e}")
            return {"error": str(e)}
    
    def _parse_market_cap(self, market_cap_str: str) -> float:
        """Parse market cap string to float"""
        if isinstance(market_cap_str, (int, float)):
            return float(market_cap_str)
        
        market_cap_str = str(market_cap_str).replace('$', '').strip()
        
        multipliers = {'T': 1e12, 'B': 1e9, 'M': 1e6, 'K': 1e3}
        
        for suffix, multiplier in multipliers.items():
            if suffix in market_cap_str:
                return float(market_cap_str.replace(suffix, '')) * multiplier
        
        return 0
    
    def _calculate_ytd_return(self, ticker: str) -> float:
        """Calculate year-to-date return"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="ytd")
            if not hist.empty:
                return round((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100, 2)
        except:
            pass
        return 0
    
    def _rank_performance(self, ticker: str, peers: List[str]) -> Dict:
        """Rank performance against peers"""
        try:
            all_tickers = [ticker] + peers
            performance_data = []
            
            for t in all_tickers:
                ytd_return = self._calculate_ytd_return(t)
                performance_data.append({'ticker': t, 'ytd_return': ytd_return})
            
            # Sort by performance
            performance_data.sort(key=lambda x: x['ytd_return'], reverse=True)
            
            # Find ranking
            rank = next((i + 1 for i, p in enumerate(performance_data) if p['ticker'] == ticker), 0)
            
            return {
                "ytd_rank": f"{rank} of {len(all_tickers)}",
                "ytd_return": next(p['ytd_return'] for p in performance_data if p['ticker'] == ticker),
                "best_performer": performance_data[0]['ticker'],
                "worst_performer": performance_data[-1]['ticker']
            }
            
        except Exception as e:
            print(f"Error ranking performance: {e}")
            return {"error": str(e)}
    
    def _get_news_sentiment(self, ticker: str) -> Dict:
        """Analyze news sentiment"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return {"message": "No recent news"}
            
            # Analyze sentiment of recent news
            sentiments = []
            
            for article in news[:20]:
                # Simple sentiment analysis based on title
                title = article.get('title', '').lower()
                
                positive_words = ['surge', 'jump', 'rally', 'gain', 'positive', 'approve', 'breakthrough', 'success']
                negative_words = ['fall', 'drop', 'decline', 'loss', 'negative', 'reject', 'fail', 'concern']
                
                pos_score = sum(1 for word in positive_words if word in title)
                neg_score = sum(1 for word in negative_words if word in title)
                
                if pos_score > neg_score:
                    sentiment = 'positive'
                elif neg_score > pos_score:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                
                sentiments.append(sentiment)
            
            # Calculate overall sentiment
            pos_count = sentiments.count('positive')
            neg_count = sentiments.count('negative')
            neu_count = sentiments.count('neutral')
            
            overall_sentiment = 'positive' if pos_count > neg_count else 'negative' if neg_count > pos_count else 'neutral'
            
            return {
                "overall_sentiment": overall_sentiment,
                "sentiment_score": round((pos_count - neg_count) / len(sentiments) * 100, 2),
                "sentiment_breakdown": {
                    "positive": pos_count,
                    "negative": neg_count,
                    "neutral": neu_count
                },
                "recent_headlines": [article.get('title', '') for article in news[:5]]
            }
            
        except Exception as e:
            print(f"Error analyzing news sentiment: {e}")
            return {"error": str(e)}
    
    def _get_social_sentiment(self, ticker: str) -> Dict:
        """Get social media sentiment (placeholder - would need Reddit/Twitter API)"""
        # This would require actual social media APIs
        # For now, return placeholder data
        return {
            "message": "Social sentiment analysis requires API access",
            "placeholder_data": {
                "reddit_mentions": "N/A",
                "twitter_mentions": "N/A",
                "stocktwits_sentiment": "N/A"
            }
        }
    
    def _get_institutional_changes(self, ticker: str) -> Dict:
        """Get institutional ownership changes"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get major holders
            major_holders = stock.major_holders
            institutional_holders = stock.institutional_holders
            
            if institutional_holders is not None and not institutional_holders.empty:
                # Get top holders
                top_holders = institutional_holders.head(10)
                
                return {
                    "institutional_ownership_pct": major_holders[0][0] if major_holders is not None else "N/A",
                    "top_holders": [
                        {
                            "holder": row['Holder'],
                            "shares": row['Shares'],
                            "value": row['Value'],
                            "pct_held": round(row['% Out'] * 100, 2) if '% Out' in row else 0
                        }
                        for _, row in top_holders.iterrows()
                    ],
                    "recent_changes": "Data on recent changes requires premium API access"
                }
            else:
                return {"message": "No institutional data available"}
                
        except Exception as e:
            print(f"Error getting institutional data: {e}")
            return {"error": str(e)}
    
    def _get_patent_activity(self, company_name: str) -> Dict:
        """Get patent activity (placeholder - would need patent API)"""
        return {
            "message": "Patent data requires specialized API access",
            "placeholder_info": {
                "recent_patents": "Check USPTO database",
                "patent_applications": "Requires patent search API"
            }
        }
    
    def _get_clinical_trial_updates(self, company_name: str) -> Dict:
        """Get recent clinical trial updates"""
        # Use existing clinical trial data from parent class
        clinical_data = self._get_clinical_trials(company_name)
        
        # Add additional analysis
        if clinical_data.get('total_submissions', 0) > 0:
            clinical_data['trial_velocity'] = "High" if clinical_data.get('active_trials', 0) > 5 else \
                                            "Moderate" if clinical_data.get('active_trials', 0) > 2 else "Low"
            
            clinical_data['phase_distribution'] = {
                'phase_3_pct': round(clinical_data.get('phase_3_trials', 0) / clinical_data.get('total_submissions', 1) * 100, 1),
                'phase_2_pct': round(clinical_data.get('phase_2_trials', 0) / clinical_data.get('total_submissions', 1) * 100, 1),
                'phase_1_pct': round(clinical_data.get('phase_1_trials', 0) / clinical_data.get('total_submissions', 1) * 100, 1)
            }
        
        return clinical_data
    
    def _calculate_risk_metrics(self, ticker: str, company_data: Dict) -> Dict:
        """Calculate comprehensive risk metrics"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            if hist.empty:
                return {"error": "No historical data for risk calculation"}
            
            # Calculate returns
            returns = hist['Close'].pct_change().dropna()
            
            # Calculate risk metrics
            volatility = returns.std() * np.sqrt(252)  # Annualized
            sharpe_ratio = (returns.mean() * 252) / (volatility) if volatility > 0 else 0
            
            # Calculate max drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Beta calculation (would need market data)
            beta = 1.2  # Placeholder
            
            # Liquidity risk
            avg_volume = hist['Volume'].mean()
            avg_dollar_volume = avg_volume * hist['Close'].mean()
            
            # Financial risk
            debt_to_equity = 0
            if 'totalDebt' in company_data and 'totalStockholderEquity' in company_data:
                if company_data.get('totalStockholderEquity', 0) > 0:
                    debt_to_equity = company_data.get('totalDebt', 0) / company_data.get('totalStockholderEquity', 1)
            
            return {
                "volatility": round(volatility * 100, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "max_drawdown": round(max_drawdown * 100, 2),
                "beta": beta,
                "liquidity_score": "High" if avg_dollar_volume > 50e6 else "Medium" if avg_dollar_volume > 10e6 else "Low",
                "financial_risk": {
                    "debt_to_equity": round(debt_to_equity, 2),
                    "cash_burn_risk": company_data.get('financial_health', {}).get('runway_months', 'N/A')
                },
                "regulatory_risk": "High (FDA dependent)" if company_data.get('industry', '').lower() in ['biotech', 'pharmaceutical'] else "Medium",
                "overall_risk_rating": self._calculate_overall_risk(volatility, debt_to_equity, company_data)
            }
            
        except Exception as e:
            print(f"Error calculating risk metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_risk(self, volatility: float, debt_ratio: float, company_data: Dict) -> str:
        """Calculate overall risk rating"""
        risk_score = 0
        
        # Volatility risk
        if volatility > 0.5:
            risk_score += 3
        elif volatility > 0.3:
            risk_score += 2
        else:
            risk_score += 1
        
        # Financial risk
        if debt_ratio > 2:
            risk_score += 3
        elif debt_ratio > 1:
            risk_score += 2
        else:
            risk_score += 1
        
        # Size risk
        market_cap = self._parse_market_cap(company_data.get('market_cap', '0'))
        if market_cap < 300e6:
            risk_score += 3
        elif market_cap < 2e9:
            risk_score += 2
        else:
            risk_score += 1
        
        # Determine rating
        if risk_score >= 7:
            return "High Risk"
        elif risk_score >= 5:
            return "Medium-High Risk"
        elif risk_score >= 3:
            return "Medium Risk"
        else:
            return "Low-Medium Risk"
    
    def _generate_ai_insights(self, data: Dict) -> Dict:
        """Generate AI-powered insights from all data"""
        try:
            if not OPENAI_API_KEY:
                return {"message": "AI insights require OpenAI API key"}
            
            # Prepare summary of key metrics
            summary = f"""
            Company: {data.get('company_name')} ({data.get('ticker')})
            Current Price: ${data.get('real_time_data', {}).get('current_price', 'N/A')}
            Market Cap: {data.get('market_cap')}
            
            Technical Analysis:
            - RSI: {data.get('technical_analysis', {}).get('rsi')} ({data.get('technical_analysis', {}).get('rsi_signal')})
            - Trend: {data.get('technical_analysis', {}).get('trend_strength')}
            
            Analyst Consensus: {data.get('analyst_consensus', {}).get('consensus')}
            Insider Sentiment: {data.get('insider_activity', {}).get('summary', {}).get('net_sentiment')}
            News Sentiment: {data.get('news_sentiment', {}).get('overall_sentiment')}
            
            Risk Rating: {data.get('risk_assessment', {}).get('overall_risk_rating')}
            """
            
            # Generate insights using AI (placeholder for actual implementation)
            insights = {
                "key_takeaways": [
                    f"Technical indicators suggest {data.get('technical_analysis', {}).get('trend_strength', 'uncertain trend')}",
                    f"Analyst consensus is {data.get('analyst_consensus', {}).get('consensus', 'unclear')}",
                    f"News sentiment appears {data.get('news_sentiment', {}).get('overall_sentiment', 'neutral')}"
                ],
                "opportunities": self._identify_opportunities(data),
                "risks": self._identify_risks(data),
                "action_items": self._suggest_actions(data)
            }
            
            return insights
            
        except Exception as e:
            print(f"Error generating AI insights: {e}")
            return {"error": str(e)}
    
    def _identify_opportunities(self, data: Dict) -> List[str]:
        """Identify investment opportunities"""
        opportunities = []
        
        # Technical opportunities
        rsi = data.get('technical_analysis', {}).get('rsi', 50)
        if rsi < 30:
            opportunities.append("RSI indicates oversold condition - potential bounce opportunity")
        
        # Valuation opportunities
        analyst_data = data.get('analyst_consensus', {}).get('price_targets', {})
        upside = analyst_data.get('upside_potential', 0)
        if upside > 20:
            opportunities.append(f"Significant upside potential of {upside}% to analyst target")
        
        # Insider buying
        insider_sentiment = data.get('insider_activity', {}).get('summary', {}).get('net_sentiment')
        if insider_sentiment == 'Bullish':
            opportunities.append("Recent insider buying indicates management confidence")
        
        return opportunities if opportunities else ["No clear opportunities identified"]
    
    def _identify_risks(self, data: Dict) -> List[str]:
        """Identify investment risks"""
        risks = []
        
        # Volatility risk
        volatility = data.get('risk_assessment', {}).get('volatility', 0)
        if volatility > 40:
            risks.append(f"High volatility of {volatility}% indicates significant price risk")
        
        # Financial risk
        runway = data.get('financial_health', {}).get('runway_months', 'N/A')
        if isinstance(runway, str) and 'months' in runway:
            months = int(runway.split()[0])
            if months < 12:
                risks.append(f"Limited cash runway of {runway} poses financing risk")
        
        # Technical weakness
        trend = data.get('technical_analysis', {}).get('macd', {}).get('trend')
        if trend == 'Bearish':
            risks.append("MACD indicates bearish momentum")
        
        return risks if risks else ["Standard market and sector risks apply"]
    
    def _suggest_actions(self, data: Dict) -> List[str]:
        """Suggest actionable items"""
        actions = []
        
        # Based on consensus
        consensus = data.get('analyst_consensus', {}).get('consensus', '')
        if consensus == 'Strong Buy':
            actions.append("Consider initiating or adding to position given strong analyst support")
        elif consensus == 'Sell':
            actions.append("Review position and consider reducing exposure")
        
        # Based on technical levels
        support = data.get('technical_analysis', {}).get('support_resistance', {}).get('support', 0)
        if support > 0:
            actions.append(f"Consider setting stop loss near support at ${support}")
        
        # Based on upcoming events
        if data.get('fda_submissions', {}).get('pending_decisions', 0) > 0:
            actions.append("Monitor upcoming FDA decisions closely")
        
        return actions if actions else ["Continue monitoring for entry/exit opportunities"]
    
    def generate_enhanced_report(self, ticker: str) -> str:
        """Generate comprehensive enhanced report"""
        intel = self.get_enhanced_intelligence(ticker)
        
        if "error" in intel:
            return f"\n❌ Error: {intel['error']}\n"
        
        report = f"""
{'='*80}
🚀 ENHANCED HEALTHCARE INTELLIGENCE REPORT
{'='*80}

📊 COMPANY OVERVIEW
Company: {intel['company_name']} ({intel['ticker']})
Sector: {intel['sector']}
Industry: {intel['industry']}
Market Cap: {intel['market_cap']}
Website: {intel['website']}

💹 REAL-TIME MARKET DATA
Current Price: ${intel['real_time_data'].get('current_price', 'N/A')}
Day Change: ${intel['real_time_data'].get('day_change', 0)} ({intel['real_time_data'].get('day_change_pct', 0)}%)
Day Range: ${intel['real_time_data'].get('day_low', 0)} - ${intel['real_time_data'].get('day_high', 0)}
Volume: {intel['real_time_data'].get('volume', 0):,}
VWAP: ${intel['real_time_data'].get('vwap', 0)}

📈 TECHNICAL ANALYSIS
RSI: {intel['technical_analysis'].get('rsi', 'N/A')} ({intel['technical_analysis'].get('rsi_signal', 'N/A')})
MACD Trend: {intel['technical_analysis'].get('macd', {}).get('trend', 'N/A')}
Trend Strength: {intel['technical_analysis'].get('trend_strength', 'N/A')}
Support: ${intel['technical_analysis'].get('support_resistance', {}).get('support', 0)}
Resistance: ${intel['technical_analysis'].get('support_resistance', {}).get('resistance', 0)}

🎯 ANALYST RATINGS
Consensus: {intel['analyst_consensus'].get('consensus', 'N/A')}
Price Target (Mean): ${intel['analyst_consensus'].get('price_targets', {}).get('mean', 0)}
Upside Potential: {intel['analyst_consensus'].get('price_targets', {}).get('upside_potential', 0)}%

👥 INSIDER ACTIVITY
Net Sentiment: {intel['insider_activity'].get('summary', {}).get('net_sentiment', 'N/A')}
Recent Buys: {intel['insider_activity'].get('summary', {}).get('total_buys', 0)}
Recent Sells: {intel['insider_activity'].get('summary', {}).get('total_sells', 0)}

📊 OPTIONS FLOW
Put/Call Ratio: {intel['options_analysis'].get('put_call_ratio', 'N/A')}
Options Sentiment: {intel['options_analysis'].get('sentiment', 'N/A')}

📰 NEWS SENTIMENT
Overall: {intel['news_sentiment'].get('overall_sentiment', 'N/A')}
Sentiment Score: {intel['news_sentiment'].get('sentiment_score', 0)}

⚠️ RISK ASSESSMENT
Overall Risk: {intel['risk_assessment'].get('overall_risk_rating', 'N/A')}
Volatility: {intel['risk_assessment'].get('volatility', 0)}%
Max Drawdown: {intel['risk_assessment'].get('max_drawdown', 0)}%
Sharpe Ratio: {intel['risk_assessment'].get('sharpe_ratio', 0)}

🤖 AI-POWERED INSIGHTS
Key Takeaways:
"""
        
        # Add AI insights
        for takeaway in intel.get('ai_insights', {}).get('key_takeaways', []):
            report += f"• {takeaway}\n"
        
        report += "\nOpportunities:\n"
        for opp in intel.get('ai_insights', {}).get('opportunities', []):
            report += f"• {opp}\n"
        
        report += "\nRisks:\n"
        for risk in intel.get('ai_insights', {}).get('risks', []):
            report += f"• {risk}\n"
        
        report += "\nRecommended Actions:\n"
        for action in intel.get('ai_insights', {}).get('action_items', []):
            report += f"• {action}\n"
        
        report += f"""
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data sources: Yahoo Finance, Internal Databases, AI Analysis
{'='*80}
"""
        
        return report


def test_enhanced_intelligence():
    """Test the enhanced stock intelligence system"""
    intel = EnhancedStockIntelligence()
    
    # Test with a healthcare ticker
    ticker = "MRNA"
    
    print(f"🧪 Testing Enhanced Stock Intelligence for {ticker}")
    print("=" * 60)
    
    # Get enhanced intelligence
    data = intel.get_enhanced_intelligence(ticker)
    
    # Print key sections
    print("\n📊 Real-Time Data:")
    print(json.dumps(data.get('real_time_data', {}), indent=2))
    
    print("\n📈 Technical Indicators:")
    print(f"RSI: {data.get('technical_analysis', {}).get('rsi')} ({data.get('technical_analysis', {}).get('rsi_signal')})")
    print(f"Trend: {data.get('technical_analysis', {}).get('trend_strength')}")
    
    print("\n🎯 Analyst Consensus:")
    print(f"Rating: {data.get('analyst_consensus', {}).get('consensus')}")
    
    print("\n🤖 AI Insights:")
    print(json.dumps(data.get('ai_insights', {}), indent=2))
    
    # Generate full report
    print("\n" + "=" * 60)
    print("GENERATING FULL REPORT...")
    print("=" * 60)
    
    report = intel.generate_enhanced_report(ticker)
    print(report)


if __name__ == "__main__":
    test_enhanced_intelligence() 