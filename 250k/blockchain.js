// Import Web3 library
const Web3 = require('web3');

// Connect to the Ethereum network (replace with your provider URL)
const web3 = new Web3('https://mainnet.infura.io/v3/YOUR-PROJECT-ID');

// Contract ABI (replace with your actual ABI)
const contractABI = [
    // ... ABI details ...
];

// Contract address (replace with your deployed contract address)
const contractAddress = '0x1234567890123456789012345678901234567890';

// Create contract instance
const agriMarketplace = new web3.eth.Contract(contractABI, contractAddress);

// Function to list a product
async function listProduct(name, price, quantity) {
    const accounts = await web3.eth.getAccounts();
    await agriMarketplace.methods.listProduct(name, price, quantity).send({ from: accounts[0] });
    console.log(`Product ${name} listed successfully`);
}

// Function to purchase a product
async function purchaseProduct(productId, value) {
    const accounts = await web3.eth.getAccounts();
    await agriMarketplace.methods.purchaseProduct(productId).send({ from: accounts[0], value: value });
    console.log(`Product ${productId} purchased successfully`);
}

// Function to get product details
async function getProduct(productId) {
    const product = await agriMarketplace.methods.getProduct(productId).call();
    console.log(`Product details: ${JSON.stringify(product)}`);
    return product;
}

// Example usage
// listProduct('Organic Apples', web3.utils.toWei('0.1', 'ether'), 100);
// purchaseProduct(1, web3.utils.toWei('0.1', 'ether'));
// getProduct(1);
