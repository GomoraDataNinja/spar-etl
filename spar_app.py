"""
SPAR ETL Receiver - SQL Server Version (Standalone)
No external config files needed - everything is here
"""

from flask import Flask, request, jsonify
from datetime import datetime
import pyodbc
import logging
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================
# SQL SERVER CONFIGURATION - UPDATE THESE!
# ============================================

# === IMPORTANT: Update these 3 settings ===
SQL_SERVER = "."  # Your SQL Server name (or "COMPUTER_NAME\SQLEXPRESS")
DATABASE_NAME = "SPAR_ETL"  # Database name you created in SSMS
USE_WINDOWS_AUTH = True  # True = Windows Auth, False = SQL Auth

# If USE_WINDOWS_AUTH = False, uncomment and fill these:
# SQL_USERNAME = "your_username"
# SQL_PASSWORD = "your_password"
# ============================================

# Statistics
stats = {
    'total_received': 0,
    'startup_time': datetime.now(),
    'last_sale': None
}

def get_connection():
    """Get SQL Server connection"""
    if USE_WINDOWS_AUTH:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SQL_SERVER};"
            f"DATABASE={DATABASE_NAME};"
            f"Trusted_Connection=yes;"
        )
    else:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SQL_SERVER};"
            f"DATABASE={DATABASE_NAME};"
            f"UID={SQL_USERNAME};"
            f"PWD={SQL_PASSWORD};"
        )
    return pyodbc.connect(conn_str)

def create_table_if_not_exists():
    """Create the sales table if it doesn't exist"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'etl_sales_raw')
            BEGIN
                CREATE TABLE etl_sales_raw (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    sale_id NVARCHAR(50) UNIQUE NOT NULL,
                    customer_name NVARCHAR(100) NOT NULL,
                    customer_email NVARCHAR(100) NULL,
                    customer_id NVARCHAR(50) NULL,
                    phone NVARCHAR(20) NULL,
                    product_category NVARCHAR(50) NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    total_sales DECIMAL(10,2) NOT NULL,
                    rewards_earned INT NOT NULL,
                    sale_date DATE NOT NULL,
                    sale_month NVARCHAR(3) NOT NULL,
                    sale_year INT NOT NULL,
                    sale_time TIME NOT NULL,
                    timestamp_utc DATETIME NOT NULL,
                    recorded_by NVARCHAR(100) NULL,
                    created_at DATETIME DEFAULT GETDATE()
                )
            END
        """)
        
        # Create index
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_sale_date' AND object_id = OBJECT_ID('etl_sales_raw'))
            BEGIN
                CREATE INDEX idx_sale_date ON etl_sales_raw(sale_date)
            END
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ Table ready: etl_sales_raw")
        return True
        
    except Exception as e:
        logger.error(f"Table creation error: {e}")
        return False

# ============================================
# WEBHOOK ENDPOINT
# ============================================

@app.route('/webhook', methods=['POST', 'OPTIONS'])
def webhook():
    """Receive data from Tengai app - saves to SQL Server"""
    
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        logger.info(f"📥 Received: {data.get('customer_name')} - ${data.get('total_sales', 0):,.2f} - Recorded by: {data.get('recorded_by', 'system')}")
        
        # Parse timestamp - handle different date fields
        if data.get('sale_date') and data.get('sale_time'):
            # Data already has sale_date and sale_time
            sale_date = data.get('sale_date')
            sale_time = data.get('sale_time')
            timestamp_str = f"{sale_date} {sale_time}"
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        elif data.get('timestamp'):
            timestamp_str = data.get('timestamp')
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timestamp_str
            sale_date = timestamp.strftime('%Y-%m-%d')
            sale_time = timestamp.strftime('%H:%M:%S')
        else:
            timestamp = datetime.now()
            sale_date = timestamp.strftime('%Y-%m-%d')
            sale_time = timestamp.strftime('%H:%M:%S')
        
        # Get month and year
        if isinstance(timestamp, datetime):
            sale_month = timestamp.strftime('%b').upper()
            sale_year = timestamp.year
        else:
            sale_month = datetime.now().strftime('%b').upper()
            sale_year = datetime.now().year
        
        # Update stats
        stats['total_received'] += 1
        stats['last_sale'] = data
        
        # Save to SQL Server
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO etl_sales_raw (
                sale_id, customer_name, customer_email, customer_id, phone,
                product_category, quantity, unit_price, total_sales, rewards_earned,
                sale_date, sale_month, sale_year, sale_time, timestamp_utc, recorded_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('sale_id'),
            data.get('customer_name'),
            data.get('customer_email', ''),
            data.get('customer_id', ''),
            data.get('phone', ''),
            data.get('product_category', data.get('product', 'General')),
            data.get('quantity', 1),
            data.get('unit_price', 0),
            data.get('total_sales', 0),
            data.get('rewards_earned', 0),
            sale_date,
            data.get('sale_month', sale_month),
            data.get('sale_year', sale_year),
            sale_time,
            timestamp if isinstance(timestamp, datetime) else datetime.now(),
            data.get('recorded_by', 'system')
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Saved to SQL Server! Total: {stats['total_received']} sales")
        
        return jsonify({
            "status": "success",
            "message": "Data saved to SQL Server",
            "sale_id": data.get('sale_id'),
            "total_sales_received": stats['total_received']
        }), 200
        
    except pyodbc.IntegrityError:
        logger.warning(f"⚠️ Duplicate sale_id: {data.get('sale_id')}")
        return jsonify({"status": "success", "message": "Duplicate ignored"}), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check for Cloudflare"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "total_received": stats['total_received'],
        "uptime_minutes": round((datetime.now() - stats['startup_time']).total_seconds() / 60, 2)
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get ETL statistics"""
    return jsonify({
        "total_received": stats['total_received'],
        "startup_time": stats['startup_time'].isoformat(),
        "last_sale": stats['last_sale']
    })

@app.route('/recent', methods=['GET'])
def recent_sales():
    """Get last 20 sales from database with full details"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 20 
                id,
                sale_id, 
                recorded_by,
                customer_name, 
                customer_email,
                customer_id,
                phone,
                product_category,
                quantity,
                unit_price,
                total_sales,
                rewards_earned,
                sale_date,
                sale_time,
                created_at
            FROM etl_sales_raw 
            ORDER BY id DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'sale_id': row[1],
                'recorded_by': row[2] if row[2] else 'Unknown',
                'customer_name': row[3],
                'customer_email': row[4] if row[4] else '',
                'customer_id': row[5] if row[5] else '',
                'phone': row[6] if row[6] else '',
                'product_category': row[7],
                'quantity': row[8],
                'unit_price': float(row[9]) if row[9] else 0,
                'total_sales': float(row[10]) if row[10] else 0,
                'rewards_earned': float(row[11]) if row[11] else 0,
                'sale_date': str(row[12]),
                'sale_time': str(row[13])[:8] if row[13] else '00:00:00',
                'created_at': str(row[14])
            })
        
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Recent sales error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/sales/today', methods=['GET'])
def today_sales():
    """Get today's sales - used by operator dashboard"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT 
                sale_id, 
                recorded_by,
                customer_name, 
                product_category,
                quantity,
                total_sales,
                sale_time
            FROM etl_sales_raw 
            WHERE sale_date = ?
            ORDER BY sale_time DESC
        """, (today,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'sale_id': row[0],
                'recorded_by': row[1] if row[1] else 'Unknown',
                'customer_name': row[2],
                'product_category': row[3],
                'quantity': row[4],
                'total_sales': float(row[5]) if row[5] else 0,
                'sale_time': str(row[6])[:8] if row[6] else '00:00:00'
            })
        
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Today sales error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/sales/operator/<operator_name>', methods=['GET'])
def operator_sales(operator_name):
    """Get sales for a specific operator"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT 
                sale_id, 
                customer_name, 
                product_category,
                quantity,
                total_sales,
                sale_time
            FROM etl_sales_raw 
            WHERE recorded_by = ? AND sale_date = ?
            ORDER BY sale_time DESC
        """, (operator_name, today))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'sale_id': row[0],
                'customer_name': row[1],
                'product_category': row[2],
                'quantity': row[3],
                'total_sales': float(row[4]) if row[4] else 0,
                'sale_time': str(row[5])[:8] if row[5] else '00:00:00'
            })
        
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Operator sales error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("🛒 SPAR ETL RECEIVER - SQL SERVER MODE")
    print("=" * 60)
    
    # Test SQL Server connection and create table
    print("\n🔍 Testing SQL Server connection...")
    try:
        conn = get_connection()
        print(f"✅ Connected to SQL Server: {SQL_SERVER}")
        conn.close()
        
        # Create table if not exists
        create_table_if_not_exists()
        
    except pyodbc.Error as e:
        print(f"\n❌ SQL Server connection failed!")
        print(f"Error: {e}")
        print("\nPlease check:")
        print("1. Is SQL Server running?")
        print("2. Is the database 'SPAR_ETL' created?")
        print("3. Do you have ODBC Driver 17 installed?")
        print("\nTo install ODBC Driver: https://aka.ms/downloadmsodbcsql")
        print("\nPress Ctrl+C to exit...")
        input()
    
    print(f"\n🚀 Starting webhook server on port 8000...")
    print(f"📍 Webhook: http://localhost:8000/webhook")
    print(f"📍 Health: http://localhost:8000/health")
    print(f"📍 Stats: http://localhost:8000/stats")
    print(f"📍 Recent: http://localhost:8000/recent")
    print(f"📍 Today's Sales: http://localhost:8000/sales/today")
    print(f"📍 Operator Sales: http://localhost:8000/sales/operator/{'name'}")
    print("\n⚠️  Keep this window open!")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8000, debug=False)


