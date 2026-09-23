from flask import Flask, render_template_string, redirect, url_for, request, flash, session
import random
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'replit_zen_system_secure_key_123')

USERS_DB = {}

def generate_heavy_transactions(bank_name):
    transactions = []
    descriptions = [
        'UPI/Ref-639201/GooglePay/Groceries', 'UPI/Ref-104958/PhonePe/FuelPump',
        'Zomato Online Order / Food', 'ATM Cash Withdrawal / Self',
        'IMPS Outward / Rent Payment', 'NEFT Inward / Salary Received',
        'UPI/Ref-774920/Paytm/Dairy', 'Amazon India Shopping Online',
        'Interest Credited / Quarterly', 'Electricity Bill Payment'
    ]
    base_date = datetime.today()
    current_balance = random.randint(50000, 200000)
    
    for i in range(1, 1501):
        t_id = f"TXN{random.randint(100000, 999999)}INR"
        amount = random.randint(50, 15000)
        desc = random.choice(descriptions)
        
        if 'Salary' in desc or 'Interest' in desc:
            t_type = 'CREDIT (CR)'
            current_balance += amount
        else:
            t_type = 'DEBIT (DR)'
            current_balance -= amount
            
        t_date = (base_date - timedelta(days=random.randint(1, 1000))).strftime('%Y-%m-%d')
        transactions.append({'date': t_date, 'bank': bank_name, 'id': t_id, 'desc': desc, 'type': t_type, 'amount': amount, 'balance': current_balance})
        
    transactions.sort(key=lambda x: x['date'])
    return transactions

LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background-color: #f8f9fa; padding: 20px; display: flex; justify-content: center; }
        .card { background: white; border: 1px solid #ccc; padding: 20px; border-radius: 8px; width: 100%; max-width: 350px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-top: 50px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; font-size: 14px; }
        .form-group input { width: 93%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        .btn { width: 100%; padding: 10px; background-color: #0d6efd; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h3 style="text-align: center; margin-bottom: 20px;">🔑 लॉगिन करें</h3>
        <form method="POST" action="/login">
            <div class="form-group"><label>यूजरनेम</label><input type="text" name="username" required></div>
            <div class="form-group"><label>पासवर्ड</label><input type="password" name="password" required></div>
            <button type="submit" class="btn">Log In</button>
        </form>
        <p style="text-align: center; margin-top: 15px; font-size: 14px;">अकाउंट नहीं है? <a href="/register">यहाँ रजिस्टर करें</a></p>
    </div>
</body>
</html>
'''

REGISTER_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background-color: #f8f9fa; padding: 20px; display: flex; justify-content: center; }
        .card { background: white; border: 1px solid #ccc; padding: 20px; border-radius: 8px; width: 100%; max-width: 350px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-top: 50px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; font-size: 14px; }
        .form-group input { width: 93%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        .btn { width: 100%; padding: 10px; background-color: #198754; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h3 style="text-align: center; margin-bottom: 20px;">📝 नया अकाउंट</h3>
        <form method="POST" action="/register">
            <div class="form-group"><label>यूजरनेम</label><input type="text" name="username" required></div>
            <div class="form-group"><label>पासवर्ड</label><input type="password" name="password" required></div>
            <div style="margin-bottom: 15px;"><input type="checkbox" name="make_admin" value="yes" id="admin_chk"> <label for="admin_chk" style="font-size: 14px;">मुझे एडमिन बनाएं</label></div>
            <button type="submit" class="btn">Sign Up</button>
        </form>
        <p style="text-align: center; margin-top: 15px; font-size: 14px;">पहले से अकाउंट है? <a href="/login">लॉगिन करें</a></p>
    </div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background-color: #f8f9fa; font-family: sans-serif; margin: 0; padding: 0; }
        .nav-header { background-color: white; border-bottom: 1px solid #e3e6f0; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .logo-box { font-weight: bold; font-size: 18px; color: #0d6efd; display: flex; align-items: center; }
        .logo-icon { background: #0d6efd; color: white; padding: 2px 6px; border-radius: 4px; margin-right: 6px; font-size: 14px; }
        .credit-badge { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 4px 12px; border-radius: 5px; text-align: center; line-height: 1.1; }
        .form-container { width: 90%; max-width: 500px; margin: 20px auto; padding-bottom: 5px; }
        .alert-box { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 12px; border-radius: 6px; margin-bottom: 25px; font-size: 13.5px; display: flex; align-items: center; }
        .project-section { text-align: center; margin-bottom: 25px; }
        .section-title { font-size: 12px; font-weight: bold; color: #6c757d; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.5px; }
        .project-btn { border: 1px solid #ccc; background: white; margin: 0 3px; padding: 6px 12px; border-radius: 5px; font-size: 13px; font-weight: bold; color: #333; }
        .project-btn.active { background-color: #0d6efd; color: white; border-color: #0d6efd; }
        .form-section { background: white; border: 1px solid #e3e6f0; border-radius: 6px; padding: 15px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .row { display: flex; gap: 10px; margin-bottom: 12px; }
        .col { flex: 1; display: flex; flex-direction: column; }
        .col label { font-size: 11px; font-weight: bold; color: #6c757d; margin-bottom: 4px; }
        .col input, .col select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }
        .full-width { display: flex; flex-direction: column; margin-bottom: 12px; }
        .full-width label { font-size: 11px; font-weight: bold; color: #6c757d; margin-bottom: 4px; }
        .full-width input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }
        .submit-btn { width: 100%; padding: 12px; background-color: #0d6efd; color: white; border: none; border-radius: 6px; font-size: 15px; font-weight: bold; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .submit-btn:disabled { background-color: #cccccc; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="nav-header">
        <div class="logo-box"><span class="logo-icon">🔳</span>GenSystem</div>
        <div style="font-size: 13px; color: #777; margin-left: -40px;">/ PDF Generator</div>
        <div class="credit-badge">
            <b style="font-size: 15px; display: block;">{{ credits }}</b>
            <span style="font-size: 9px; text-transform: uppercase; color: #555;">credits</span>
        </div>
    </div>
    <div class="form-container">
        {% if credits < 2 %}
        <div class="alert-box">
            <span style="font-size: 18px; margin-right: 8px;">⚠️</span>
            No credits remaining. You need 2 credits to generate a PDF. Contact your admin.
        </div>
        {% endif %}
        <div class="project-section">
            <div class="section-title">Select Project</div>
            <button type="button" class="project-btn active">PB Shop</button>
            <button type="button" class="project-btn">PB SL</button>
            <button type="button" class="project-btn">SB Shop</button>
            <button type="button" class="project-btn">SB SAL</button>
        </div>
        <form method="GET" action="/download/report">
            <input type="hidden" name="selected_bank" value="YES BANK">
            <div class="form-section">
                <div class="section-title" style="color: #333; margin-bottom: 12px;"><input type="checkbox" checked disabled> ACCOUNT</div>
                <div class="row">
                    <div class="col"><label>ACCOUNT NUMBER</label><input type="text" placeholder="16-digit" required></div>
                    <div class="col"><label>OPENING BALANCE (₹)</label><input type="number" placeholder="0.00" required></div>
                </div>
                <div class="row">
                    <div class="col"><label>START DATE</label><input type="date" name="start_date" required></div>
                    <div class="col"><label>END DATE</label><input type="date" name="end_date" required></div>
                </div>
            </div>
            <div class="form-section">
                <div class="section-title" style="color: #333; margin-bottom: 12px;"><input type="radio" checked disabled> CUSTOMER</div>
                <div class="row">
                    <div class="col"><label>CUSTOMER NAME</label><input type="text" placeholder="Name" required></div>
                    
