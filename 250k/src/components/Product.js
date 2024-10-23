import React, { useState, useEffect } from 'react';
import { getProduct, updatePrice } from '../services/api';
import { subscribeToProduct, unsubscribeFromProduct } from '../services/socket';
import { initBlockchain, purchaseProduct } from '../services/blockchain';

const Product = ({ productId }) => {
  const [product, setProduct] = useState(null);
  const [web3, setWeb3] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      const data = await getProduct(productId);
      setProduct(data);
    };

    fetchProduct();

    subscribeToProduct(productId, (data) => {
      setProduct(prevProduct => ({ ...prevProduct, ...data }));
    });

    return () => {
      unsubscribeFromProduct(productId);
    };
  }, [productId]);

  useEffect(() => {
    initBlockchain();
  }, []);

  const handleUpdatePrice = async () => {
    await updatePrice(productId);
  };

  const handlePurchase = async () => {
    try {
      await purchaseProduct(productId, web3.utils.toWei(product.price, 'ether'));
      alert('Purchase successful!');
    } catch (error) {
      console.error('Purchase failed:', error);
      alert('Purchase failed. Check console for details.');
    }
  };

  if (!product) return <div>Loading...</div>;

  return (
    <div>
      <h2>{product.name}</h2>
      <p>Price: ${product.price}</p>
      <p>Quantity: {product.quantity}</p>
      <p>Seller: {product.seller}</p>
      <button onClick={handleUpdatePrice}>Update Price</button>
      <button onClick={handlePurchase}>Purchase</button>
    </div>
  );
};

export default Product;
