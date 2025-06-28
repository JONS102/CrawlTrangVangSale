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

def crawl_trangvang(nganh_hang, khu_vuc, page_start=1, page_end=10):
    base_url = "https://trangvangvietnam.com/"
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    nganh_hang_url = to_slug(nganh_hang)
    khu_vuc_url = to_slug(khu_vuc)
    for page in range(page_start, page_end+1):
        url = f"{base_url}srch/{khu_vuc_url}/{nganh_hang_url}.html?page={page}"
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            # Phát hiện encoding thực tế
            detected = chardet.detect(resp.content)
            resp.encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            time.sleep(1)
            if resp.status_code != 200:
                print(f"Không truy cập được {url}, status: {resp.status_code}")
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            company_divs = soup.select('div.div_list_cty > div.w-100.h-auto.shadow.rounded-3.bg-white.p-2.mb-3')
            print(f"Trang {page}: tìm thấy {len(company_divs)} mục")
            if not company_divs:
                break
            for comp in company_divs:
                # Tên công ty
                name_tag = comp.select_one('div.listings_center h2 a, div.listings_center_khongxacthuc h2 a')
                name = name_tag.get_text(strip=True) if name_tag else ''
                
                # Địa chỉ - cải thiện để lấy chính xác hơn
                addresses = []
                # Tìm địa chỉ trong logo_congty_diachi
                address_divs = comp.select('div.logo_congty_diachi > div, div.listing_diachi_nologo > div')
                for div in address_divs:
                    txt = div.get_text(strip=True)
                    # Lọc địa chỉ chính (có chứa Việt Nam, TP., Tỉnh, hoặc các từ khóa địa chỉ)
                    if ('Việt Nam' in txt or 'TP.' in txt or 'Tỉnh' in txt or 
                        'Quận' in txt or 'Huyện' in txt or 'Phường' in txt or 
                        'Xã' in txt or 'ấp' in txt or 'Đường' in txt or 
                        'Khu' in txt or 'Lô' in txt) and len(txt) > 10:
                        addresses.append(txt)
                
                # Lấy địa chỉ đầu tiên làm địa chỉ chính
                address = addresses[0] if addresses else ''
                
                # Số điện thoại - cải thiện để lấy tất cả số điện thoại
                phones = []
                
                # Tìm tất cả số điện thoại trong div chứa thông tin liên hệ
                phone_divs = comp.select('div.logo_congty_diachi, div.listing_diachi_nologo')
                for phone_div in phone_divs:
                    # Tìm tất cả thẻ a có href="tel:..."
                    phone_links = phone_div.select('a[href^="tel:"]')
                    for link in phone_links:
                        phone_text = link.get_text(strip=True)
                        if phone_text and len(phone_text) >= 8:  # Số điện thoại phải có ít nhất 8 ký tự
                            phones.append(phone_text)
                
                # Loại bỏ số trùng lặp
                phones = list(dict.fromkeys(phones))
                phone = ', '.join(phones) if phones else ''
                
                # Email
                email = ''
                email_tag = comp.select_one('div.email_web_section a[href^="mailto:"]')
                if email_tag:
                    email = email_tag.get('href', '').replace('mailto:', '').strip()
                
                # Website
                website = ''
                website_tag = comp.select_one('div.email_web_section a[href^="http"]')
                if website_tag:
                    website = website_tag.get('href', '').strip()
                
                # Mô tả - cải thiện để lấy đầy đủ hơn
                description = ''
                desc_tag = comp.select_one('div.div_textqc small.text_qc')
                if desc_tag:
                    # Lấy text và giữ nguyên format
                    description = desc_tag.get_text(separator=' ', strip=True)
                    # Loại bỏ các ký tự HTML entities
                    description = re.sub(r'&#\d+;', '', description)
                    description = re.sub(r'&[a-zA-Z]+;', '', description)
                
                results.append({
                    'Tên Khách Hàng': name,
                    'Số điện thoại': phone,
                    'Địa chỉ': address,
                    'Email': email,
                    'Website': website,
                    'Mô tả': description
                })
        except Exception as e:
            print(f"Lỗi khi crawl {url}: {e}")
            continue
    print(f"Tổng số mục tìm được: {len(results)}")
    return results

@app.route('/', methods=['GET'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Template error: {str(e)}',
            'template_folder': app.template_folder
        })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'Application is running'})

@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        nganh_hang = request.form.get('nganh_hang')
        khu_vuc = request.form.get('khu_vuc')
        page_start = int(request.form.get('page_start', 1))
        page_end = int(request.form.get('page_end', 10))
        export_type = request.form.get('export_type', 'excel')
        data = crawl_trangvang(nganh_hang, khu_vuc, page_start, page_end)
        if not data:
            data = [{
                'Tên Khách Hàng': 'Không tìm thấy dữ liệu',
                'Số điện thoại': '',
                'Địa chỉ': '',
                'Email': '',
                'Website': '',
                'Mô tả': ''
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

# For Vercel
app = app

if __name__ == "__main__":
    app.run()
