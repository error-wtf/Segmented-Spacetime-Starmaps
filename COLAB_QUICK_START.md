# 🌌 SSZ Explorer - Google Colab Quick Start

**Run SSZ Explorer directly in your browser - no installation needed!**

---

## 🚀 One-Click Launch

1. **Open Colab Notebook:**  
   [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/error-wtf/Segmented-Spacetime-Starmaps/blob/main/SSZ_Explorer_Colab.ipynb)

2. **Run all cells:**  
   Click `Runtime → Run all` (or press `Ctrl+F9`)

3. **Wait for Gradio link:**  
   After ~2-3 minutes, a **public link** will appear (ends with `.gradio.live`)

4. **Click the link & explore!**  
   The app runs for 72 hours

---

## 📋 What You Get

✅ **Interactive Sky Maps**
- 2D full-sky view (500k GAIA stars)
- 3D rotatable view
- Constellation zoom

✅ **SSZ Physics Visualizations**
- g₁/g₂ domain structure (φ-based segment density)
- Time dilation comparison (SSZ vs GR)
- Radial stretch analysis

✅ **Object Search & Selection**
- Search by name: `Sag A*`, `Betelgeuse`, `M31`
- Search by coordinates
- Detailed physics for any object

✅ **Data Enrichment**
- AKARI infrared data integration
- ESO/ALMA spectroscopy
- Real-time statistics

---

## 💡 Tips

**First Time Using Colab?**
- Google Colab is a free Jupyter notebook service
- No account required (but recommended for saving work)
- GPU/TPU available for free!

**Gradio Link Expired?**
- Just re-run the last cell to generate a new link
- Or restart the entire notebook

**App Running Slow?**
- Colab free tier has limited resources
- Try reducing number of stars in settings
- Close other Colab notebooks

---

## 🔧 Local Installation (Full Features)

For unlimited stars, faster performance, and offline use:

```bash
git clone https://github.com/error-wtf/Segmented-Spacetime-Starmaps.git
cd Segmented-Spacetime-Starmaps/ssz_explorer
pip install -r requirements.txt
python gradio_app_complete.py
```

Open `http://localhost:7860` in your browser.

---

## 📚 Learn More

- **Physics Background:** [SSZ Theory Integration](ssz_explorer/SSZ_METRIC_PURE_INTEGRATION.md)
- **Full Documentation:** [README.md](README.md)
- **Feature Guide:** [Usage Guide](ssz_explorer/QUICK_REFERENCE.md)

---

## 🐛 Troubleshooting

**Gradio link not appearing?**
- Wait 2-3 minutes for installation
- Check for error messages in output
- Try `Runtime → Restart runtime` and run again

**"Module not found" errors?**
- Ensure all cells executed successfully
- Check Step 2 (Install Dependencies) completed

**App crashes or freezes?**
- Colab free tier memory limited
- Try using smaller star database (50k instead of 500k)

---

## 📧 Support & Feedback

**Found a bug?** Open an issue on GitHub  
**Have a suggestion?** Start a discussion  
**Want to contribute?** Pull requests welcome!

**Authors:** Carmen Wrede, Lino Casu, Bingsi  
**License:** ACSL v1.4  
**Repository:** https://github.com/error-wtf/Segmented-Spacetime-Starmaps

---

🌌 **Enjoy exploring the segmented spacetime universe!** ✨
