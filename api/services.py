from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

class SoliqVerificationError(Exception):
    def __init__(self, message, raw_response=None):
        self.message = message
        self.raw_response = raw_response
        super().__init__(self.message)

def verify_soliq_receipt(url):
    """
    Fetches a Soliq QR code URL and extracts data via HTML scraping.
    """
    try:
        # Extract basic info from the URL to build the receipt_id and date
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # We still need receipt number & date from URL for our unique constraints
        if 'r' not in query_params or 'c' not in query_params:
            raise SoliqVerificationError("Invalid QR code format. Missing receipt number or date.")
            
        receipt_number = query_params['r'][0]
        datetime_str = query_params['c'][0]
        
        # Format the date properly into a standard timestamp
        formatted_date = f"{datetime_str[:4]}-{datetime_str[4:6]}-{datetime_str[6:8]}T{datetime_str[8:10]}:{datetime_str[10:12]}:{datetime_str[12:14]}Z"
        
        # Now fetch the actual webpage to get the TIN and Total Amount safely
        # Use a comprehensive set of headers to bypass basic bot protection on Render
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        tin = None
        total_amount = None

        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check if receipt is marked as fake by Soliq
                if "Chek qalbaki ravishda yaratilgan" in response.text:
                     raise SoliqVerificationError("This receipt is marked as fraudulent (qalbaki) by Soliq.")
                
                # 1. Extract TIN - Highly robust text search approach
                # Soliq has multiple receipt formats. Some put TIN in <i>, some in a labeled <td>
                tds = soup.find_all('td')
                for idx, td in enumerate(tds):
                    text = td.text.strip()
                    # Check for "Komitent STIR" or similar labels
                    if 'STIR' in text or 'INN' in text or 'СТИР' in text or 'ИНН' in text:
                        # Look ahead in the next few cells for a 9 or 14 digit number
                        for offset in range(1, 4):
                            if idx + offset < len(tds):
                                cand_text = tds[idx + offset].text.strip()
                                # 9 digits (TIN) or 14 digits (PINFL)
                                import re
                                if re.match(r'^\d{9}$', cand_text) or re.match(r'^\d{14}$', cand_text):
                                    tin = cand_text
                                    break
                        if tin: break

                # Fallback to the old method: looking for an isolated <i> tag with exactly 9 digits
                if not tin:
                    i_tags = soup.find_all('i')
                    for i in i_tags:
                        text = i.text.strip()
                        import re
                        if re.match(r'^\d{9}$', text):
                            tin = text
                            break
                        
                # 2. Extract Total Amount (Jami to'lov)
                for idx, td in enumerate(tds):
                    if td.text and ("Jami to`lov:" in td.text or "Jami to'lov:" in td.text or "Итого:" in td.text):
                        # The user's provided HTML shows the amount is in the IMMEDIATE next td element
                        if idx + 1 < len(tds):
                            candidate = tds[idx + 1].text.strip()
                            # Clean up spaces and commas e.g., "30,000.00" -> "30000.00"
                            cand_clean = candidate.replace(',', '').replace(' ', '')
                            try:
                                total_amount = float(cand_clean)
                                break
                            except ValueError:
                                # Look a bit further just in case there are empty cells
                                for offset in range(2, 4):
                                    if idx + offset < len(tds):
                                        c = tds[idx + offset].text.strip().replace(',', '').replace(' ', '')
                                        try:
                                            total_amount = float(c)
                                            break
                                        except ValueError:
                                            pass
                        if total_amount is not None:
                            break
        except requests.RequestException:
            pass # Request failed, fallback to URL logic below
            
        # 3. Final validation
        if not tin:
             raise SoliqVerificationError("Could not locate the TIN (Tax ID) on the digital receipt HTML. Scraping might be blocked or HTML format changed.")
        if total_amount is None:
             raise SoliqVerificationError("Could not locate the Total Amount on the digital receipt HTML. Scraping might be blocked or HTML format changed.")

        return {
            "receipt_id": f"soliq_{tin}_{receipt_number}_{datetime_str}",
            "receipt_number": receipt_number,
            "tin": tin,
            "total_amount": total_amount,
            "created_at": formatted_date
        }

    except requests.RequestException as e:
        raise SoliqVerificationError(f"Network error when verifying receipt: {str(e)}")
    except ValueError:
        raise SoliqVerificationError("Invalid QR code format. Missing or malformed data.")
    except Exception as e:
        if isinstance(e, SoliqVerificationError):
            raise
        raise SoliqVerificationError(str(e))
