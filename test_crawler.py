from bs4 import BeautifulSoup
import re
import pandas as pd

def clean_text(text):
    """Làm sạch text, loại bỏ HTML entities và ký tự đặc biệt"""
    if not text:
        return ''
    # Loại bỏ HTML entities
    text = re.sub(r'&#\d+;', '', text)
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    # Loại bỏ ký tự đặc biệt không cần thiết
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_phones(comp):
    """Trích xuất tất cả số điện thoại từ một đơn vị"""
    phones = []
    
    # Tìm tất cả thẻ a có href="tel:..." trong toàn bộ đơn vị
    phone_links = comp.select('a[href^="tel:"]')
    for link in phone_links:
        phone_text = link.get_text(strip=True)
        # Lọc số điện thoại hợp lệ
        if phone_text and len(phone_text) >= 8:
            # Loại bỏ các ký tự không phải số và dấu ngoặc
            clean_phone = re.sub(r'[^\d\(\)\-\s]', '', phone_text)
            if len(clean_phone) >= 8:
                phones.append(phone_text)
    
    # Loại bỏ số trùng lặp
    phones = list(dict.fromkeys(phones))
    return phones

def extract_addresses(comp):
    """Trích xuất tất cả địa chỉ từ một đơn vị"""
    addresses = []
    
    # Tìm tất cả div chứa thông tin địa chỉ
    address_divs = comp.select('div.logo_congty_diachi > div, div.listing_diachi_nologo > div')
    
    for div in address_divs:
        txt = div.get_text(strip=True)
        # Lọc địa chỉ chính (có chứa từ khóa địa chỉ)
        if ('Việt Nam' in txt or 'TP.' in txt or 'Tỉnh' in txt or 
            'Quận' in txt or 'Huyện' in txt or 'Phường' in txt or 
            'Xã' in txt or 'ấp' in txt or 'Đường' in txt or 
            'Khu' in txt or 'Lô' in txt or 'Số' in txt) and len(txt) > 10:
            addresses.append(clean_text(txt))
    
    return addresses

def extract_description(comp):
    """Trích xuất mô tả từ một đơn vị"""
    desc_tag = comp.select_one('div.div_textqc small.text_qc')
    if desc_tag:
        description = desc_tag.get_text(separator=' ', strip=True)
        return clean_text(description)
    return ''

def extract_contact_info(comp):
    """Trích xuất thông tin liên hệ (email, website)"""
    email = ''
    website = ''
    
    # Tìm email
    email_tag = comp.select_one('div.email_web_section a[href^="mailto:"]')
    if email_tag:
        email = email_tag.get('href', '').replace('mailto:', '').strip()
    
    # Tìm website
    website_tag = comp.select_one('div.email_web_section a[href^="http"]')
    if website_tag:
        website = website_tag.get('href', '').strip()
    
    return email, website

def test_crawl_from_file(filename):
    """Test crawl từ file HTML có sẵn"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        company_divs = soup.select('div.div_list_cty > div.w-100.h-auto.shadow.rounded-3.bg-white.p-2.mb-3')
        
        print(f"Tìm thấy {len(company_divs)} đơn vị trong file {filename}")
        
        results = []
        for i, comp in enumerate(company_divs[:5]):  # Chỉ test 5 đơn vị đầu
            print(f"\n--- Đơn vị {i+1} ---")
            
            # Tên công ty
            name_tag = comp.select_one('div.listings_center h2 a, div.listings_center_khongxacthuc h2 a')
            name = clean_text(name_tag.get_text(strip=True)) if name_tag else ''
            print(f"Tên: {name}")
            
            # Trích xuất thông tin
            phones = extract_phones(comp)
            addresses = extract_addresses(comp)
            description = extract_description(comp)
            email, website = extract_contact_info(comp)
            
            print(f"Số điện thoại: {phones}")
            print(f"Địa chỉ: {addresses}")
            print(f"Email: {email}")
            print(f"Website: {website}")
            print(f"Mô tả: {description[:100]}...")
            
            # Tạo kết quả
            result = {
                'Tên Khách Hàng': name,
                'Số điện thoại': ', '.join(phones) if phones else '',
                'Địa chỉ': addresses[0] if addresses else '',
                'Địa chỉ bổ sung': ', '.join(addresses[1:]) if len(addresses) > 1 else '',
                'Email': email,
                'Website': website,
                'Mô tả': description
            }
            
            results.append(result)
        
        # Lưu kết quả test
        df = pd.DataFrame(results)
        df.to_csv('test_result.csv', index=False, encoding='utf-8-sig')
        print(f"\nĐã lưu kết quả test vào file test_result.csv")
        
        return results
        
    except Exception as e:
        print(f"Lỗi khi test: {e}")
        return []

if __name__ == "__main__":
    # Test với file HTML có sẵn
    test_crawl_from_file('nhựa các công ty nhựa ở tại long an(page ).html') 