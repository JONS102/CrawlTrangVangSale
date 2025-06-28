# CrawlTrangVangSale
Crawl Trang Vàng - Web scraping application for TrangVang Vietnam

## Deployment to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Login to Vercel: `vercel login`
3. Deploy: `vercel --prod`

## Local Development

1. Install requirements: `pip install -r requirements.txt`
2. Run app: `python app.py`
3. Open: http://localhost:5000

## Files Structure
- `app.py` - Main Flask application
- `index.py` - Entry point for Vercel
- `vercel.json` - Vercel configuration
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version for Vercel
- `templates/` - HTML templates