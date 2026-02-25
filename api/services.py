from urllib.parse import urlparse, parse_qs

class SoliqVerificationError(Exception):
    def __init__(self, message, raw_response=None):
        self.message = message
        self.raw_response = raw_response
        super().__init__(self.message)

def verify_soliq_receipt(url):
    """
    Parses a Soliq QR code URL and simulates validation.
    URL format: https://ofd.soliq.uz/check?t=UZ123456789&r=1&c=20250221120000&s=150000.00
    """
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Required parameters according to Soliq spec
        # t = TIN (INN)
        # r = receipt number (fiskal belgi)
        # c = datetime
        # s = sum/total amount
        
        if 't' not in query_params or 'r' not in query_params or 'c' not in query_params or 's' not in query_params:
            raise SoliqVerificationError("Invalid QR code format.")
            
        tin = query_params['t'][0]
        receipt_number = query_params['r'][0]
        datetime_str = query_params['c'][0]
        amount_str = query_params['s'][0]
        
        # Simulate API check (in reality, you'd make an HTTP request to OFD)
        # For our simulation, we'll assume valid if format is correct
        
        total_amount = float(amount_str)
        # Assuming the date format is YYYYMMDDHHMMSS
        formatted_date = f"{datetime_str[:4]}-{datetime_str[4:6]}-{datetime_str[6:8]}T{datetime_str[8:10]}:{datetime_str[10:12]}:{datetime_str[12:14]}Z"
        
        return {
            "receipt_id": f"soliq_{tin}_{receipt_number}_{datetime_str}",
            "receipt_number": receipt_number,
            "tin": tin,
            "total_amount": total_amount,
            "created_at": formatted_date
        }
    except ValueError:
        raise SoliqVerificationError("Invalid QR code format.")
    except Exception as e:
        if isinstance(e, SoliqVerificationError):
            raise
        raise SoliqVerificationError(str(e))
