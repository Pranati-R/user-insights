# Quick Reference - Anomaly Detection & File Upload

## 🚀 Quick Start

### Upload a File
1. Go to File Upload page
2. Select file (CSV, JSON, PSI, TSV, TXT, LOG)
3. Click "Upload & process"
4. View results with anomaly detection

### Train Custom Model
```bash
cd backend
python train/train_anomaly_model.py
```

### Adjust Sensitivity
Edit `.env`:
```env
ANOMALY_SCORE_THRESHOLD=0.65  # 0.5=sensitive, 0.8=strict
```

## 📊 What You'll See After Upload

### Processing Stats
- ✅ Successfully processed events
- ❌ Failed events (if any)
- 📊 Total events in file
- 📈 Success rate %

### Anomaly Breakdown
- 🚨 Total anomalies
- 📊 Anomaly percentage
- 📋 Top patterns
- 💡 Why flagged

## 🎯 Anomaly Reasons Explained

| Reason | What It Means | Action |
|--------|---------------|--------|
| Very short session | < 10 seconds | Possible bot |
| High click rate | > 80% clicks | Suspicious behavior |
| Rapid events | < 0.5s between | Bot-like speed |
| Single page focus | 20+ events, 1 page | Scraper/bot |
| High frequency | > 2 events/second | Automated |

## 🔧 Common Tasks

### Check Anomaly Rate
- **< 5%** = Normal (green)
- **5-15%** = Moderate (yellow)
- **> 15%** = High (red, investigate)

### Improve Detection
1. Train on more data
2. Adjust threshold
3. Add custom features
4. Review false positives

### Debug Issues
```bash
# Check model exists
ls backend/app/models/local_iforest.pkl

# View logs
tail -f backend/logs/app.log

# Test upload
curl -X POST http://localhost:8000/api/upload-file \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.csv"
```

## 📈 Performance Tips

### For Large Files
- Split into chunks < 50MB
- Upload during off-peak hours
- Monitor memory usage

### For Better Accuracy
- Train on 1000+ sessions
- Include diverse data
- Retrain monthly
- Monitor false positives

## 🎨 UI Components

### Anomaly Breakdown Card
- Shows anomaly rate with color coding
- Lists top 5 patterns
- Displays detection confidence
- Provides recommendations

### Processing Stats Cards
- Success count (green)
- Failed count (red, if any)
- Total count (blue)
- Success rate %

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| No anomalies detected | Lower threshold to 0.5 |
| Too many false positives | Raise threshold to 0.75 |
| Model not loading | Run training script |
| Upload fails | Check file format |
| Slow processing | Reduce file size |

## 📚 Documentation Links

- **Full Guide**: `ANOMALY_DETECTION_IMPROVEMENTS.md`
- **File Upload**: `FILE_UPLOAD_GUIDE.md`
- **Implementation**: `IMPROVEMENTS_SUMMARY.md`
- **API Docs**: `http://localhost:8000/docs`

## ⚡ Keyboard Shortcuts

- Upload page: `/upload`
- Dashboard: `/dashboard`
- Sessions: `/sessions`
- Anomalies: `/anomalies`

## 💡 Pro Tips

1. **Train regularly** - Retrain monthly for best results
2. **Monitor trends** - Track anomaly rate over time
3. **Tune threshold** - Adjust based on your needs
4. **Review flagged** - Check top anomalies manually
5. **Use Groq AI** - Add API key for better parsing

---

**Need Help?** Check the full documentation or run:
```bash
python backend/train/train_anomaly_model.py --help
```
