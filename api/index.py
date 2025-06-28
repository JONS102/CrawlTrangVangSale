from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup
import re
import time
import unicodedata
import chardet
import os

app = Flask(__name__, template_folder='../templates')

def to_slug(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = text.replace(' ', '_').replace('-', '_').lower()
    return text

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Template error: {str(e)}',
            'template_folder': app.template_folder
        })

@app.route('/health')
def health():
    return jsonify({'status': 'OK', 'message': 'Application is running'})

@app.route('/test')
def test():
    return jsonify({
        'message': 'Hello from Vercel!',
        'status': 'success',
        'app_name': 'CrawlTrangVangSale'
    })

# Simplified crawl function for testing
def crawl_trangvang_simple(nganh_hang, khu_vuc, page_start=1, page_end=2):
    """Simplified version with fewer requests for testing"""
    results = []
    base_url = "https://trangvangvietnam.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    nganh_hang_url = to_slug(nganh_hang)
    khu_vuc_url = to_slug(khu_vuc)
    
    for page in range(page_start, min(page_end + 1, page_start + 2)):  # Limit to 2 pages max
        url = f"{base_url}srch/{khu_vuc_url}/{nganh_hang_url}.html?page={page}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)  # Reduced timeout
            if resp.status_code != 200:
                continue
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            company_divs = soup.select('div.div_list_cty > div.w-100.h-auto.shadow.rounded-3.bg-white.p-2.mb-3')
            
            for comp in company_divs[:5]:  # Limit to 5 companies per page
                name_tag = comp.select_one('div.listings_center h2 a, div.listings_center_khongxacthuc h2 a')
                name = name_tag.get_text(strip=True) if name_tag else 'N/A'
                
                # Simple phone extraction
                phone_links = comp.select('a[href^="tel:"]')
                phones = [link.get_text(strip=True) for link in phone_links[:2]]  # Limit to 2 phones
                phone = ', '.join(phones) if phones else 'N/A'
                
                results.append({
                    'Tên Khách Hàng': name,
                    'Số điện thoại': phone,
                    'Địa chỉ': 'N/A',  # Simplified
                    'Email': 'N/A',
                    'Website': 'N/A',
                    'Mô tả': 'N/A'
                })
                
            time.sleep(0.5)  # Reduced sleep time
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            continue
            
    return results

@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        nganh_hang = request.form.get('nganh_hang', 'test')
        khu_vuc = request.form.get('khu_vuc', 'ho-chi-minh')
        page_start = int(request.form.get('page_start', 1))
        page_end = int(request.form.get('page_end', 2))
        export_type = request.form.get('export_type', 'csv')
        
        # Use simplified crawl function
        data = crawl_trangvang_simple(nganh_hang, khu_vuc, page_start, page_end)
        
        if not data:
            data = [{
                'Tên Khách Hàng': 'Không tìm thấy dữ liệu',
                'Số điện thoại': 'N/A',
                'Địa chỉ': 'N/A',
                'Email': 'N/A',
                'Website': 'N/A',
                'Mô tả': 'N/A'
            }]
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        
        if export_type == 'csv':
            df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            return send_file(output, download_name='ket_qua.csv', as_attachment=True)
        else:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            return send_file(output, download_name='ket_qua.xlsx', as_attachment=True)
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Crawl error: {str(e)}'
        })

# Vercel entry point
if __name__ == "__main__":
    app.run()