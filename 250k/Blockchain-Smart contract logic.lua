// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AgriMarketplace {
    struct Product {
        uint256 id;
        string name;
        uint256 price;
        uint256 quantity;
        address payable seller;
    }

    mapping(uint256 => Product) public products;
    uint256 public productCount;

    event ProductListed(uint256 indexed id, string name, uint256 price, uint256 quantity, address seller);
    event ProductPurchased(uint256 indexed id, string name, uint256 price, uint256 quantity, address buyer, address seller);

    function listProduct(string memory _name, uint256 _price, uint256 _quantity) public {
        require(_price > 0, "Price must be greater than zero");
        require(_quantity > 0, "Quantity must be greater than zero");

        productCount++;
        products[productCount] = Product(productCount, _name, _price, _quantity, payable(msg.sender));
        emit ProductListed(productCount, _name, _price, _quantity, msg.sender);
    }

    function purchaseProduct(uint256 _id) public payable {
        Product storage product = products[_id];
        require(product.id > 0 && product.id <= productCount, "Product does not exist");
        require(product.quantity > 0, "Product is out of stock");
        require(msg.value >= product.price, "Insufficient funds sent");

        product.seller.transfer(product.price);
        product.quantity--;

        emit ProductPurchased(product.id, product.name, product.price, 1, msg.sender, product.seller);

        if (msg.value > product.price) {
            payable(msg.sender).transfer(msg.value - product.price);
        }
    }

    function getProduct(uint256 _id) public view returns (uint256, string memory, uint256, uint256, address) {
        require(_id > 0 && _id <= productCount, "Product does not exist");
        Product memory product = products[_id];
        return (product.id, product.name, product.price, product.quantity, product.seller);
    }
}
