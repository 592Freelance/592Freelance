import Web3 from 'web3';

let web3;
let contract;

export const initBlockchain = async () => {
  if (window.ethereum) {
    web3 = new Web3(window.ethereum);
    try {
      await window.ethereum.enable();
    } catch (error) {
      console.error("User denied account access");
    }
  } else if (window.web3) {
    web3 = new Web3(window.web3.currentProvider);
  } else {
    console.log('Non-Ethereum browser detected. Consider trying MetaMask!');
  }

  const contractAddress = '0x1234567890123456789012345678901234567890'; // Replace with your contract address
  const contractABI = []; // Replace with your contract ABI

  contract = new web3.eth.Contract(contractABI, contractAddress);
};

export const purchaseProduct = async (productId, value) => {
  const accounts = await web3.eth.getAccounts();
  await contract.methods.purchaseProduct(productId).send({ from: accounts[0], value: value });
};
