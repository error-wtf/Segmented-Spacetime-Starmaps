---
title: SSZ Interactive3D Viewer
emoji: 🌌
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: other
---

# 🌌 SSZ Interactive3D Viewer

**Interactive 3D Visualization of Segmented Spacetime Physics with Real GAIA DR3 Data**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/error-wtf/Segmented-Spacetime-Starmaps)
[![License](https://img.shields.io/badge/License-ACSL%20v1.4-red)](https://github.com/error-wtf/Segmented-Spacetime-Starmaps/blob/main/LICENSE)

---

## ✨ Features

- 🌟 **Real GAIA DR3 Data**: Access to 1.8 billion stars
- 📊 **Interactive Visualizations**: 5-tab interface
- ⚖️ **SSZ vs GR Comparison**: Compare theoretical predictions
- 🔬 **Pure SSZ Physics**: Explore golden ratio spacetime
- 🎯 **Galactic Center Queries**: Search specific regions
- 📈 **Statistics**: Dataset information and metrics
- 📁 **Data Export**: Download results (CSV/JSON)

---

## 🚀 Quick Start

### **Tab 1: Load GAIA Data**
1. Select number of stars (10-1000)
2. Toggle "Use Real GAIA Data" for real astronomical data
3. Click "Load Data"
4. View sample in table

### **Tab 2: SSZ vs GR Comparison**
1. Select stellar mass (0.1-100 M☉)
2. Choose plot type:
   - Time Dilation
   - Velocity Comparison  
   - Orbital Period
3. Click "Generate Plot"
4. Compare SSZ (blue) vs GR (red)

### **Tab 3: SSZ Physics**
1. Select stellar mass
2. Choose visualization:
   - Radial Profiles
   - 3D Segment Field
   - Time Dilation Map
3. Click "Generate Plot"
4. Explore pure SSZ physics

### **Tab 4: Galactic Center**
1. Set search radius (0.1-5.0 degrees)
2. Click "Search"
3. View stars near Sgr A*
4. Check brightest stars table

### **Tab 5: Statistics**
1. Click "Get Statistics"
2. View dataset metrics
3. Check data quality
4. Review sources

---

## 🔬 Scientific Background

### **Segmented Spacetime (SSZ)**

SSZ is an alternative theory of gravity featuring:

**Key Formulas:**
```
Segment Density:  Ξ(r) = 1 - exp(-φ · r/r_s)
Time Dilation:    D_SSZ = 1/(1 + Ξ)
Golden Ratio:     φ = (1+√5)/2 ≈ 1.618
```

**Unique Properties:**
- ✅ No singularities at event horizons
- ✅ Golden ratio as fundamental constant
- ✅ Testable predictions vs GR
- ✅ Finite black hole properties
- ✅ Observable differences in strong fields

---

## 📊 Data Sources

### **GAIA DR3** (Primary)
- **Source**: ESA GAIA Mission
- **Objects**: 1.8 billion stars
- **Data**: Positions, parallaxes, photometry, proper motions
- **Access**: Via astroquery
- **Fallback**: Synthetic data if unavailable

### **Synthetic Data** (Backup)
- **Generated**: Realistic stellar population
- **Purpose**: Testing and offline use
- **Quality**: Validates algorithms
- **Transition**: Seamless fallback

---

## 🎯 Use Cases

### **Research:**
- Validate SSZ predictions
- Compare with GR
- Test observational data
- Generate hypotheses
- Publish results

### **Education:**
- Learn SSZ physics
- Explore real data
- Interactive demonstrations
- Classroom use
- Student projects

### **Exploration:**
- Discover patterns
- Query regions
- Visualize spacetime
- Export for analysis
- Share findings

---

## 📈 Performance

```
Query Time:    ~1-2 seconds (100-1k stars)
Cache:         224x speedup on repeated queries
SSZ Calc:      0.1-10 µs per object
Memory:        <100 MB typical usage
Uptime:        24/7 on HuggingFace
```

---

## 🛠️ Technical Stack

```
Framework:     Gradio 4.0+
Backend:       Python 3.10+
Data:          Pandas, NumPy
Astronomy:     astroquery, astropy
Visualization: Plotly
Physics:       Custom SSZ implementation
```

---

## 📚 Documentation

**Full Documentation:**
- [GitHub Repository](https://github.com/error-wtf/Segmented-Spacetime-Starmaps)
- [GAIA Integration Guide](https://github.com/error-wtf/Segmented-Spacetime-Starmaps/blob/main/Interactive3D_ssz_viewer/GAIA_INTEGRATION.md)
- [User Manual](https://github.com/error-wtf/Segmented-Spacetime-Starmaps/blob/main/Interactive3D_ssz_viewer/INTERACTIVE_SKYMAP_GUIDE.md)
- [Quick Reference](https://github.com/error-wtf/Segmented-Spacetime-Starmaps/blob/main/Interactive3D_ssz_viewer/QUICK_REFERENCE.md)

---

## 🤝 Contributing

We welcome contributions!

**Ways to Contribute:**
- Report bugs
- Suggest features  
- Improve documentation
- Share results
- Star the repository

**GitHub:** https://github.com/error-wtf/Segmented-Spacetime-Starmaps

---

## 🎓 Citation

If you use this tool in your research:

```bibtex
@software{ssz_Interactive3D_viewer_2025,
  title={SSZ Interactive3D Viewer: Interactive Visualization Platform for Segmented Spacetime Physics},
  author={Wrede, Carmen and Casu, Lino},
  year={2025},
  url={https://github.com/error-wtf/Segmented-Spacetime-Starmaps},
  note={Version 1.0}
}
```

---

## 📞 Contact & Support

**Questions?**
- 📖 Check [Documentation](https://github.com/error-wtf/Segmented-Spacetime-Starmaps)
- 🐛 Report [Issues](https://github.com/error-wtf/Segmented-Spacetime-Starmaps/issues)
- 💬 Join [Discussions](https://github.com/error-wtf/Segmented-Spacetime-Starmaps/discussions)

**Collaboration:**
- Research partnerships welcome
- Observatory integration possible
- Educational use encouraged

---

## 📄 License

**ANTI-CAPITALIST SOFTWARE LICENSE v1.4**

- ✅ Personal use
- ✅ Educational use
- ✅ Research use
- ✅ Non-profit use
- ❌ Commercial use (requires permission)

© 2025 Carmen Wrede, Lino Casu

---

## 🌟 Acknowledgments

**Built With:**
- ESA GAIA Mission data
- astroquery & astropy
- Plotly visualization
- Gradio framework
- HuggingFace Spaces

**Inspired By:**
- General Relativity
- Golden Ratio mathematics
- Open Science principles
- Community collaboration

---

## 🚀 Future Development

**Coming Soon:**
- Multi-catalog integration (SIMBAD, 2MASS, WISE)
- Exoplanet database
- Galaxy catalogs
- Advanced visualizations
- Mobile app
- VR/AR support

**Roadmap:** [MASTERPLAN](https://github.com/error-wtf/Segmented-Spacetime-Starmaps/blob/main/Interactive3D_ssz_viewer/MASTERPLAN_TO_PERFECTION.md)

---

## 🎊 Project Status

```
Phase 1-3:  ✅ Complete (Base system)
Phase 4:    70% Complete (Real data integration)
Sprint 1:   ✅ Complete!

Status:     Production Beta
Quality:    Excellent
Performance: Optimized (224x cache)
Tests:      100% passing
```

---

**Explore the universe with SSZ physics!** 🌌✨

**Made with 💙 for the advancement of science**
