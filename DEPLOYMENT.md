# Vercel Deployment Guide

## Tùy chọn 1: Deploy qua Vercel Dashboard
1. Truy cập https://vercel.com
2. Login và chọn "Add New Project"
3. Import repository từ GitHub
4. Vercel sẽ tự động detect Python app

## Tùy chọn 2: Cài đặt Vercel CLI
```bash
npm install -g vercel
vercel login
vercel --prod
```

## Structure hiện tại:
```
├── api/
│   └── index.py          # Main Flask app
├── templates/
│   └── index.html        # HTML template
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel config (minimal)
└── README.md
```

## Endpoints:
- `/` - Trang chủ
- `/health` - Health check
- `/test` - Test endpoint
- `/crawl` - POST endpoint để crawl data

## Notes:
- File vercel.json hiện tại là `{}` để tránh warning về builds
- App được tối ưu hóa cho Vercel serverless limits
- Crawl function được simplified để tránh timeout
