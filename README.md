[![CI/CD Workflow](https://github.com/software-students-fall2023/5-final-project-ensemble/actions/workflows/CICD.yml/badge.svg)](https://github.com/software-students-fall2023/5-final-project-ensemble/actions/workflows/CICD.yml)

# SKU Tracker

This webapp allows a user to track products and how stocked the products are. The user can add products to the database, and then add stock to the products. The user can also view the products and their stock levels.

## Instructions

1. Clone the repository
2. Change directory to the repository
3. Create a .env similar to the .env.example file
4. Use docker-compose to run the application
5. The application will be running on localhost:3000
6. Open localhost:3000 in your browser
7. You can now use the application
8. To stop the application, use docker-compose down

```bash
git clone
cd 5-final-project-ensemble
cp .env.example .env
docker-compose up --build
```

## Usage

Once running the application, you can use the application by opening localhost:3000 in your browser. You must register and create an account. Then login to your respective account. You can then add products to the database using their SKU, Name, and stock. You can adjust the stock of the products or adjust any information about the product. You can also delete products from the database.

## Docker

Link for docker image: [Docker Hub](https://hub.docker.com/repository/docker/verse1/sku-tracker)

## Example of The Running Application

[Example](http://161.35.180.124:3000/)

## Authors

- [Nawaf](https://github.com/Verse1)
- [Geoffrey](https://github.com/geoffreybudiman91)
- [Alessandro](https://github.com/alessandrolandi)
- [Shreyas](https://github.com/ShreyasUjagar)
