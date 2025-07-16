# 🚀 BH Worldwide AI Dashboard

**Professional AI-powered logistics and AOG (Aircraft on Ground) management dashboard for BH Worldwide.**

## 📊 Dashboard Features

- **Executive Overview**: Financial KPIs, business health indicators, and strategic insights
- **Live AOG Center**: Mission-critical operations command center for global AOG response
- **Global Operations Map**: Interactive worldwide logistics visualization
- **Flight Status Monitor**: Real-time flight tracking and status updates
- **AI Quote Engine**: Intelligent pricing and quoting system
- **Analytics & Insights**: Advanced business intelligence and performance metrics
- **Competitive Intelligence**: Market analysis and competitive positioning
- **ROI Calculator**: Financial modeling and investment analysis tools

## 🌍 Live Demo

**Streamlit Cloud URL**: https://your-app.streamlit.app (after deployment)

## 🚀 Quick Start

### Option 1: Streamlit Cloud (Recommended for Singapore users)

1. **Fork this repository** on GitHub
2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select this repository
   - Set main file: `app.py`
   - Click "Deploy"
3. **Access your dashboard** at the provided URL

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bh-worldwide-dashboard
cd bh-worldwide-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

**Access locally at**: http://localhost:8501

## 📁 Project Structure

```
BH_Dashboard_Minimal/
├── app.py                           # Main Streamlit application
├── requirements.txt                 # Python dependencies  
├── README.md                        # This file
└── BH_Worldwide_Logistics/          # Core data directory
    ├── Customer_Data/
    │   └── Airlines/
    │       ├── extended_customers.json
    │       └── major_customers.json
    ├── Operations/
    │   ├── AOG_Center/
    │   │   ├── extended_aog_cases.json
    │   │   └── active_cases.json
    │   ├── Inventory/
    │   │   ├── extended_inventory.json
    │   │   └── critical_parts.json
    │   ├── Parts_Database/
    │   │   ├── aircraft_parts_catalog.json
    │   │   ├── parts_pricing.json
    │   │   └── inventory_locations.json
    │   └── Pricing/
    │       └── current_pricing_model.json
    ├── Business_Intelligence/
    │   ├── Competitors/
    │   │   └── competitor_analysis.json
    │   └── Pain_Points/
    │       └── current_challenges.json
    └── Financial/
        ├── Lost_Opportunities/
        │   ├── historical_analysis.json
        │   └── monthly_analysis.json
        └── BH_Actual_Financials/
            └── financial_summary.json
```

## 💡 Dashboard Navigation

1. **🏠 Executive Overview**: Start here for high-level business insights
2. **⚡ Live AOG Center**: Mission control for aircraft emergencies
3. **🗺️ Global Operations Map**: Worldwide logistics visualization
4. **✈️ Flight Status Monitor**: Real-time flight tracking
5. **🤖 AI Quote Engine**: Intelligent pricing system
6. **📊 Analytics & Insights**: Business performance metrics
7. **🎯 Competitive Intelligence**: Market positioning analysis
8. **💰 ROI Calculator**: Financial modeling tools

## 🔧 Technical Requirements

- **Python**: 3.9 or higher
- **Streamlit**: 1.46.1+
- **Memory**: 512MB RAM minimum
- **Storage**: 50MB disk space

## 📊 Data Sources

- **Real Financial Data**: BH Worldwide actual financials (2019-2024)
- **Operational Data**: Simulated AOG cases, inventory, and logistics data
- **Market Intelligence**: Competitive analysis and industry benchmarks
- **Customer Data**: Airline customer profiles and relationships

## 🔐 Data Security

- ✅ All data is demonstration-safe
- ✅ No sensitive customer information
- ✅ Financial data from public filings
- ✅ Operational scenarios are simulated

## 🆘 Troubleshooting

### Common Issues:

**1. "Cannot find BH_Worldwide_Logistics data directory"**
```bash
# Ensure directory structure is correct
ls BH_Worldwide_Logistics/
```

**2. "Session state error"**
```bash
# Refresh the browser page
# Clear browser cache if needed
```

**3. "Module not found"**
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

### Getting Help:

- 📧 **Email**: hussein.srour@thakralone.com
- 💼 **LinkedIn**: [Hussein Srour Profile](https://www.linkedin.com/in/hussein-srour)
- 🏢 **Organization**: Thakral One, Australia

## 🚀 Deployment Notes

### For Streamlit Cloud:
- Repository size: ~25MB (optimized)
- Build time: 2-3 minutes
- Memory usage: ~200MB runtime
- Auto-scales based on usage

### For Local Development:
- Supports hot-reload for development
- Full feature set available
- Direct file system access

## 📈 Performance

- **Load Time**: < 5 seconds on Streamlit Cloud
- **Interactive Charts**: Real-time updates with Plotly
- **Data Processing**: Cached for optimal performance
- **Mobile Responsive**: Works on tablets and phones

## 🔄 Updates and Versions

- **Current Version**: 1.0.0
- **Last Updated**: July 2025
- **Compatibility**: Python 3.9-3.12
- **Browser Support**: Chrome, Firefox, Safari, Edge

## 📞 Contact & Support

**Developed by**: Hussein Srour, PhD, MBA  
**Title**: Vice President, Data Science & AI Consulting  
**Organization**: Thakral One, Australia  
**LinkedIn**: [Connect Here](https://www.linkedin.com/in/hussein-srour)

---

*This dashboard demonstrates AI-powered transformation for BH Worldwide's AOG logistics operations using real financial data and simulated operational scenarios.*