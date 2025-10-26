-- E-Commerce Order System Database Schema
-- Design Goal: Support products, shopping cart, orders, and inventory management

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for username and email lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);


-- ============================================
-- ADDRESSES TABLE
-- ============================================
CREATE TABLE addresses (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state_province VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for finding user's addresses
CREATE INDEX idx_addresses_user_id ON addresses(user_id);
-- Index for finding primary address quickly
CREATE INDEX idx_addresses_user_primary ON addresses(user_id, is_primary) WHERE is_primary = true;


-- ============================================
-- PRODUCTS TABLE
-- ============================================
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_price CHECK (price >= 0)
);

-- Index for product search by name
CREATE INDEX idx_products_name ON products(name);


-- ============================================
-- INVENTORY TABLE
-- ============================================
CREATE TABLE inventory (
    product_id BIGINT PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    quantity_available INT NOT NULL DEFAULT 0,
    reserved_quantity INT NOT NULL DEFAULT 0,
    low_stock_threshold INT DEFAULT 10,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent negative stock
    CONSTRAINT positive_quantity CHECK (quantity_available >= 0),
    CONSTRAINT positive_reserved CHECK (reserved_quantity >= 0)
);

-- Index for finding low stock items
CREATE INDEX idx_inventory_low_stock ON inventory(quantity_available) 
    WHERE quantity_available <= low_stock_threshold;


-- ============================================
-- ORDERS TABLE
-- ============================================
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    
    -- Snapshot shipping address (preserves historical data)
    shipping_street VARCHAR(255) NOT NULL,
    shipping_city VARCHAR(255) NOT NULL,
    shipping_state VARCHAR(100),
    shipping_postal_code VARCHAR(20) NOT NULL,
    shipping_country VARCHAR(100) NOT NULL,
    
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    
    -- Denormalized totals for performance
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_total DECIMAL(10, 2) NOT NULL,
    grand_total DECIMAL(10, 2) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_status CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')),
    CONSTRAINT positive_totals CHECK (subtotal >= 0 AND tax_total >= 0 AND grand_total >= 0)
);

-- Index for user's order history (most common query)
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);
-- Index for admin dashboard filtering by status
CREATE INDEX idx_orders_status ON orders(status, created_at DESC);


-- ============================================
-- ORDER_ITEMS TABLE
-- ============================================
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    
    -- Snapshot product data at time of purchase
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price_at_purchase DECIMAL(10, 2) NOT NULL,
    tax_rate_at_purchase DECIMAL(5, 4) NOT NULL,
    
    CONSTRAINT positive_quantity CHECK (quantity > 0),
    CONSTRAINT positive_price CHECK (price_at_purchase >= 0)
);

-- Index for finding items in an order
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
-- Index for product sales analytics
CREATE INDEX idx_order_items_product_id ON order_items(product_id);


-- ============================================
-- CART_ITEMS TABLE
-- ============================================
CREATE TABLE cart_items (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate products in cart
    CONSTRAINT unique_cart_item UNIQUE (user_id, product_id),
    CONSTRAINT positive_cart_quantity CHECK (quantity > 0)
);

-- Index for loading user's cart
CREATE INDEX idx_cart_items_user_id ON cart_items(user_id);


-- ============================================
-- EXAMPLE QUERIES
-- ============================================

-- Get user's cart with current product info and availability
SELECT 
    ci.id,
    ci.quantity,
    p.id as product_id,
    p.name,
    p.price,
    p.image_url,
    i.quantity_available,
    (ci.quantity * p.price) as line_total
FROM cart_items ci
JOIN products p ON ci.product_id = p.id
JOIN inventory i ON p.id = i.product_id
WHERE ci.user_id = ?
ORDER BY ci.created_at;


-- Check inventory and reserve stock (ATOMIC OPERATION - use in transaction)
UPDATE inventory 
SET 
    quantity_available = quantity_available - ?,
    reserved_quantity = reserved_quantity + ?
WHERE product_id = ? 
  AND quantity_available >= ?
RETURNING product_id, quantity_available;


-- Create order from cart (simplified - would be in transaction)
INSERT INTO orders (
    user_id, 
    shipping_street, 
    shipping_city, 
    shipping_state,
    shipping_postal_code, 
    shipping_country,
    subtotal, 
    tax_total, 
    grand_total
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
RETURNING id;

-- Insert order items (from cart)
INSERT INTO order_items (
    order_id,
    product_id,
    product_name,
    quantity,
    price_at_purchase,
    tax_rate_at_purchase
)
SELECT 
    ? as order_id,
    p.id,
    p.name,
    ci.quantity,
    p.price,
    0.08 as tax_rate  -- Would come from tax calculation service
FROM cart_items ci
JOIN products p ON ci.product_id = p.id
WHERE ci.user_id = ?;


-- Get user's order history with totals
SELECT 
    o.id,
    o.status,
    o.grand_total,
    o.created_at,
    COUNT(oi.id) as item_count
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE o.user_id = ?
GROUP BY o.id
ORDER BY o.created_at DESC
LIMIT 20;


-- Get order details with all items
SELECT 
    o.*,
    oi.product_name,
    oi.quantity,
    oi.price_at_purchase,
    (oi.quantity * oi.price_at_purchase) as line_total
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE o.id = ?;


-- Find products with low stock
SELECT 
    p.id,
    p.name,
    i.quantity_available,
    i.low_stock_threshold
FROM products p
JOIN inventory i ON p.id = i.product_id
WHERE i.quantity_available <= i.low_stock_threshold
ORDER BY i.quantity_available ASC;

