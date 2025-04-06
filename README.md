# Chat with Your Database

This project demonstrates how to use natural language to interact with your Supabase database using MCP (Model Context Protocol). Instead of writing complex SQL queries, you can simply ask questions in plain English and get insights from your data.

## Features

- 🗣️ Natural language queries to your database
- 📊 Instant business analytics and insights
- 🔍 Complex SQL generation from simple questions
- 📈 Data visualization capabilities
- 🔐 Secure database access through Supabase

## Example Use Cases

Here are some real examples of insights you can get just by chatting with your database:

### 1. Sales Analytics
Ask questions like:
- "How are our monthly sales trending?"
- "What's our average order value?"

Example insight:
```
Monthly revenue: $1.1M-$1.3M
Average order value: Increased from $5,200 to $7,000
Monthly active customers: 120-140
```

### 2. Product Performance
Ask questions like:
- "Which product categories perform best?"
- "What's our inventory status?"

Example insight:
```
Top Categories by Revenue:
1. Electronics ($1.70M)
2. Sports ($1.67M)
3. Grocery ($1.67M)
```

### 3. Customer Segmentation
Ask questions like:
- "How are our customers segmented?"
- "What's the value of each customer segment?"

Example insight:
```
Customer Segments:
- Heavy users (13+ orders): 148 customers, $79,365 avg. value
- Medium users (6-10 orders): 49 customers, $53,110 avg. value
- Light users (1-5 orders): 3 customers, $27,884 avg. value
```

## Getting Started

### Prerequisites
1. A Supabase account and project
2. Your Supabase project credentials
3. Python 3.8 or higher
4. Cursor IDE with MCP extension

### Setup

1. Clone this repository:
```bash
git clone https://github.com/mayankkapoor/chat-with-database.git
cd chat-with-database
```

2. Create a `.env` file with your Supabase credentials:
See sample .env file.

3. Initialize your database:
```sql
-- Create tables
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    name TEXT,
    email TEXT NOT NULL UNIQUE,
    city TEXT,
    signup_date DATE
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC CHECK (price >= 0),
    category TEXT,
    stock_quantity INTEGER CHECK (stock_quantity >= 0)
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    quantity INTEGER CHECK (quantity > 0),
    order_status TEXT,
    order_date TIMESTAMPTZ NOT NULL
);
```

4. Generate test data:
```bash
# Install required Python packages
pip install python-dotenv supabase faker

# Run the data generation script
python populate_db.py
```

This will create:
- 400 sample users
- 500 products across 10 categories
- 2,500 orders with realistic patterns

5. Open the project in Cursor IDE and start chatting with your database!

Example questions to try:
- "Show me the monthly sales trends"
- "Which product categories have the highest revenue?"
- "What's our customer segmentation?"
- "Which products need restocking?"

## Benefits of Using MCP for Database Chat

1. **No SQL Knowledge Required**
   - Business users can get insights without knowing SQL
   - Data analysts can work faster by using natural language
   - Complex queries are generated automatically

2. **Instant Business Intelligence**
   - Get immediate answers to business questions
   - Perform ad-hoc analysis without setting up BI tools
   - Discover insights that might be missed in traditional reporting

3. **Time Savings**
   - Queries that would take 30+ minutes to write can be generated instantly
   - No need to remember table structures or relationships
   - Quick iteration on analysis questions

4. **Accessibility**
   - Makes database insights available to non-technical team members
   - Reduces dependency on data team for basic analytics
   - Enables self-service business intelligence

## Security

- All database access is managed through Supabase's security rules
- Queries are executed with appropriate role-based permissions
- Sensitive data can be protected through RLS policies

## Acknowledgments

- Supabase for providing the database infrastructure
- MCP for enabling natural language database interactions

