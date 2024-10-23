// Import required modules
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

// Initialize Express app
const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Serve static files (if needed)
app.use(express.static('public'));

// Socket.io connection handling
io.on('connection', (socket) => {
    console.log('A user connected');

    // Handle joining a product room
    socket.on('join_product_room', (productId) => {
        socket.join(`product_${productId}`);
        console.log(`User joined room for product ${productId}`);
    });

    // Handle real-time price updates
    socket.on('update_price', (data) => {
        const { productId, newPrice, supplierId } = data;
        // Here you would typically update the price in the database
        // For this example, we'll just broadcast the new price to all users in the room
        io.to(`product_${productId}`).emit('price_updated', {
            productId,
            newPrice,
            supplierId
        });
    });

    // Handle new orders
    socket.on('place_order', (data) => {
        const { buyerId, listingId, quantity, totalPrice } = data;
        // Here you would typically create the order in the database
        // For this example, we'll just emit a notification to the supplier
        const supplierId = getSupplierId(listingId); // You'd need to implement this function
        io.to(`user_${supplierId}`).emit('new_order', {
            buyerId,
            listingId,
            quantity,
            totalPrice
        });
    });

    // Handle inventory updates
    socket.on('update_inventory', (data) => {
        const { listingId, newQuantity } = data;
        // Here you would typically update the inventory in the database
        // For this example, we'll just broadcast the update to all users
        io.emit('inventory_updated', {
            listingId,
            newQuantity
        });
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        console.log('A user disconnected');
    });
});

// Start the server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

// Example of how to use this in your frontend JavaScript:
/*
const socket = io();

// Join a product room
socket.emit('join_product_room', productId);

// Listen for price updates
socket.on('price_updated', (data) => {
    console.log(`New price for product ${data.productId}: $${data.newPrice} by supplier ${data.supplierId}`);
    // Update UI with new price information
});

// Update a price (for suppliers)
socket.emit('update_price', { productId: 123, newPrice: 50.00, supplierId: 456 });

// Place an order (for buyers)
socket.emit('place_order', { buyerId: 789, listingId: 101, quantity: 5, totalPrice: 250.00 });

// Listen for new orders (for suppliers)
socket.on('new_order', (data) => {
    console.log(`New order received: ${data.quantity} units from buyer ${data.buyerId}`);
    // Display order notification in UI
});

// Update inventory (for suppliers)
socket.emit('update_inventory', { listingId: 101, newQuantity: 95 });

// Listen for inventory updates
socket.on('inventory_updated', (data) => {
    console.log(`Inventory updated for listing ${data.listingId}: ${data.newQuantity} units available`);
    // Update UI with new inventory information
});
*/

