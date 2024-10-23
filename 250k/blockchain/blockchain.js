const { Product } = require('../agri_app/models');

async function syncProductWithBlockchain(productId) {
    const product = await Product.objects.get(id=productId);
    await listProduct(product.name, web3.utils.toWei(product.price.toString(), 'ether'), product.quantity);
}

module.exports = {
    listProduct,
    purchaseProduct,
    getProduct,
    syncProductWithBlockchain
};
