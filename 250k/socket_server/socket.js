const { Product } = require('../agri_app/models');

io.on('connection', (socket) => {
    // ... existing code ...

    socket.on('update_price', async (data) => {
        const { productId, newPrice } = data;
        const product = await Product.objects.get(id=productId);
        product.price = newPrice;
        await product.save();

        io.to(`product_${productId}`).emit('price_updated', {
            productId,
            newPrice
        });
    });

    // ... existing code ...
});
