import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const getProduct = async (productId) => {
  const response = await axios.get(`${API_URL}/get-product/${productId}/`);
  return response.data;
};

export const updatePrice = async (productId) => {
  const response = await axios.post(`${API_URL}/update-price/${productId}/`);
  return response.data;
};

