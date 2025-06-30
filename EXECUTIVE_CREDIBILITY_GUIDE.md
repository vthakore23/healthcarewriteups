# 🕵️ Executive Credibility Checker Guide

## Overview

The Executive Credibility Checker is a standalone tool that allows you to research specific executives and companies to see their track record of promises vs. delivery. This tool provides detailed accountability reports showing what executives promised, when they promised it, and whether they delivered.

## Installation

The tool is included with the Healthcare Investment Intelligence Platform. No additional installation required.

## Usage

### Basic Commands

```bash
# Search for executives or companies
python check_executive_credibility.py search "John Smith"
python check_executive_credibility.py search "BioPharma"

# Check specific executive (requires company name)
python check_executive_credibility.py check "John Smith" --company "BioPharma Inc"

# Check company-wide credibility
python check_executive_credibility.py company "BioPharma Inc"

# Export detailed report
python check_executive_credibility.py export "John Smith" --company "BioPharma Inc" --output report.txt
```

### Examples

#### 1. Search for an Executive
```bash
$ python check_executive_credibility.py search "Smith"

🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 
EXECUTIVE CREDIBILITY CHECKER
Management Truth Tracker™
🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 🕵️ 

🔍 Found 3 executive(s):
------------------------------------------------------------
1. John Smith - CEO at BioPharma Inc
2. Sarah Smith - CFO at MedTech Corp
3. Robert Smith - CMO at GeneTx
```

#### 2. Check Executive Credibility
```bash
$ python check_executive_credibility.py check "John Smith" --company "BioPharma Inc"

================================================================================
EXECUTIVE: John Smith
COMPANY: BioPharma Inc
================================================================================

📊 CREDIBILITY SCORE: [████████░░░░░░░░░░░░] 40.0%
   🚨 LOW CREDIBILITY - High risk of failure/delays

📈 TRACK RECORD:
   Total Promises: 12
   ✅ On Time: 3 (25.0%)
   ⚠️  Late: 2 (16.7%)
   ❌ Failed: 7 (58.3%)
   ⏳ Pending: 0
   📅 Average Delay: 73.0 days

❌ FAILED PROMISES (7 total):
--------------------------------------------------------------------------------

1. Fda Submission
   Date: 2024-01-15
   Promise: "We expect to submit our NDA for XYZ-123 to the FDA by Q3 2024..."
   Deadline: 2024-09-30 (MISSED)
   What happened: Company announced 2-month delay in submission
   Confidence level: expect to

2. Data Readout
   Date: 2024-02-01
   Promise: "Our Phase 3 data readout will definitely be completed by June 2024..."
   Deadline: 2024-06-30 (MISSED)
   What happened: Company announced 2-month delay in data readout
   Confidence level: will definitely

💡 INVESTMENT IMPLICATIONS:
--------------------------------------------------------------------------------
🚨 This executive has poor credibility
   • High risk of delays and failures
   • Consider reducing exposure ahead of key milestones
   • Verify all claims independently
```

#### 3. Company-Wide Analysis
```bash
$ python check_executive_credibility.py company "BioPharma Inc"

================================================================================
COMPANY: BioPharma Inc
================================================================================

📊 COMPANY CREDIBILITY: [██████████░░░░░░░░░░] 48.5%
   Total Executives Tracked: 4
   Total Promises: 37

📈 PERFORMANCE BY PROMISE TYPE:
   • Clinical Timeline: 45% success (11 promises)
   • Fda Submission: 33% success (6 promises)
   • Data Readout: 50% success (8 promises)
   • Manufacturing: 67% success (3 promises)
   • Product Launch: 25% success (4 promises)
```

## Understanding the Output

### Credibility Score

The credibility score is calculated based on promise delivery:
- **Delivered on time**: 100% credit
- **Delivered late**: 50% credit
- **Failed**: 0% credit

Score interpretation:
- **80-100%**: ✅ HIGH CREDIBILITY - Reliable track record
- **60-79%**: ⚠️ MODERATE CREDIBILITY - Some delays/issues
- **Below 60%**: 🚨 LOW CREDIBILITY - High risk of failure/delays

### Promise Types

The system tracks various types of promises:
- **Clinical Timeline**: Trial enrollment, completion dates
- **FDA Submission**: NDA/BLA filing dates
- **Data Readout**: Results announcement dates
- **Partnership**: Deal completion timelines
- **Revenue Guidance**: Financial targets
- **Product Launch**: Commercial launch dates

### Red Flags

The tool highlights several red flags:
- Low credibility score (<50%)
- More failures than successes
- Chronic delays (average >60 days)
- Overdue pending promises

## Integration with Daily Reports

The Executive Credibility Checker is fully integrated with the daily intelligence reports:

1. **Automatic Analysis**: Every executive mentioned in news is automatically analyzed
2. **Inline Warnings**: Low-credibility executives are flagged in reports
3. **Detailed Sections**: Full credibility reports for executives with issues
4. **Failed Promise Details**: Specific examples of what they lied about

## Investment Applications

### Risk Management
- Size positions based on management credibility
- Add timeline buffers for low-credibility teams
- Monitor high-risk promises closely

### Due Diligence
- Research management before investing
- Compare credibility across competitors
- Track improvement/deterioration over time

### Event Trading
- Anticipate delays from chronic late-deliverers
- Position for volatility around promise deadlines
- Identify reliable management teams

## Advanced Features

### Export Reports
Generate detailed reports for investment committees:
```bash
python check_executive_credibility.py export "John Smith" --company "BioPharma Inc"
```

### Batch Analysis
Check multiple executives or companies:
```bash
# Create a file with names
echo "John Smith,BioPharma Inc" > executives.csv
echo "Jane Doe,MedTech Corp" >> executives.csv

# Run batch analysis (coming soon)
python check_executive_credibility.py batch executives.csv
```

## Tips for Effective Use

1. **Regular Monitoring**: Check executives quarterly to track changes
2. **Pre-Investment**: Always check management before new positions
3. **Event Preparation**: Review credibility before major catalysts
4. **Cross-Reference**: Compare promises with actual news to verify
5. **Pattern Recognition**: Look for language patterns in promises

## Database Management

The credibility database is stored locally in `management_promises.db`. To backup:
```bash
cp management_promises.db management_promises_backup_$(date +%Y%m%d).db
```

## Troubleshooting

### No results found
- Check spelling of executive/company names
- Try partial names (e.g., "Smith" instead of "John Smith")
- Company names must match exactly for executive checks

### Database errors
- Ensure write permissions in current directory
- Check disk space
- Run database integrity check (coming soon)

## Future Enhancements

Planned features:
- Web interface for easier access
- Automated alerts for overdue promises
- Peer comparison tools
- Historical credibility trends
- Integration with SEC filings

---

**Remember**: This tool provides data to inform decisions, not replace judgment. Always consider the full context when evaluating management credibility. 