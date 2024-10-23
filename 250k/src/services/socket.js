import io from 'socket.io-client';

const socket = io('http://localhost:3000');

export const subscribeToProduct = (productId, callback) => {
  socket.on(`product_${productId}`, (data) => {
    callback(data);
  });
  socket.emit('join_product_room', productId);
};

export const unsubscribeFromProduct = (productId) => {
  socket.off(`product_${productId}`);
};
