stocks_dict = {
    "AAPL": {"company_name": "Apple Inc.", "price": 150.23},
    "GOOG": {"company_name": "Alphabet Inc.", "price": 2500.67},
    "TSLA": {"company_name": "Tesla, Inc.", "price": 700.54},
    "MSFT": {"company_name": "Microsoft Corporation", "price": 300.10},
    "AMZN": {"company_name": "Amazon.com, Inc.", "price": 3500.15},
    "FB": {"company_name": "Facebook, Inc.", "price": 330.50},
    "JPM": {"company_name": "JPMorgan Chase & Co.", "price": 160.75},
    "JNJ": {"company_name": "Johnson & Johnson", "price": 170.85},
    "V": {"company_name": "Visa Inc.", "price": 250.35},
    "PG": {"company_name": "Procter & Gamble Company", "price": 140.40},
    "WMT": {"company_name": "Walmart Inc.", "price": 140.25},
    "BAC": {"company_name": "Bank of America Corporation", "price": 40.80},
    "MA": {"company_name": "Mastercard Incorporated", "price": 380.90},
    "KO": {"company_name": "The Coca-Cola Company", "price": 55.30},
    "DIS": {"company_name": "Walt Disney Company", "price": 175.60},
    "VZ": {"company_name": "Verizon Communications Inc.", "price": 55.75},
    "CSCO": {"company_name": "Cisco Systems, Inc.", "price": 50.20},
    "INTC": {"company_name": "Intel Corporation", "price": 55.90},
    "NFLX": {"company_name": "Netflix, Inc.", "price": 540.20},
    "IBM": {"company_name": "IBM", "price": 140.15}
}


def display_stocks(stocks_dict):
    for key, value in stocks_dict.items():
        print(f"Symbol: {key} | Company Name: {value['company_name']} /n")