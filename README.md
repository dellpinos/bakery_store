# Bakery Store

This app is a marketplace where users can order homemade dishes, and at the same time, access a "Seller Panel" to create and offer their own products. The app is focused on homemade food businesses but could be expanded to other areas.

When accessing the dashboard, a user can create their own **products**. To make price calculations dynamic and adaptable to all kinds of supplies (different prices based on quantity or size), the user can also create **ingredients** that will be available to include as part of each **product**.

New products have a **production time** since it can vary depending on the item and the seller's capacity. They also have a base price to cover "labor costs" or supplies that are not being calculated through the ingredients. The final price of the product is calculated as the sum of the base price plus the quantity of each **ingredient** used.

On the dashboard, users can also go to "Settings" to configure the maximum number of **products** they can deliver/prepare per day. This number is flexible since not all users have the same **production capacity**. At the same time, users can select "days off," which are disabled days on their calendar, allowing them to schedule vacations or breaks. There’s also a button to disable all published **products**, as long as these **products** are not part of any pending orders.

Another option in the dashboard is "Pendings", where all **pending orders** are listed. Here, the user can confirm or cancel **orders**. Once confirmed, the buyer can change their **status** to delivered, and later, the seller can archive these **orders**. **Archived** orders remain visible to both users but are not counted in the seller’s **calendar**.

The buyer user has access to the full "Product list" on the app and can use **categories** as filters to make searching easier. Once they view a product and decide to buy it, it is added to the **cart**. The user can select as many products as they want from the same seller, as long as it doesn’t exceed the seller’s daily production limit.

At "Checkout", the user can adjust the quantities of each product (while considering the seller's maximum production limit) and select a **delivery date**. The selectable dates are those not disabled by the seller and do not exceed the seller’s daily production **capacity**.

Once the order is completed, both the buyer and the seller are notified. When the seller accepts the order, the buyer can mark it as "delivered" to finalize it. Afterward, the seller can also archive the order so it becomes available in "Archived Deliveries".

## User's Workflow

Seller Workflow:

* Create an account and access the "Seller Panel".
* Create one or more ingredients with their price and quantity per package (the quantity is used to calculate the fractional value).
* Create a product with a base price, ingredients, and production time.
* Optional: set up "days off" and/or a daily production limit.
* When a buyer places an order, the seller gets a notification and a new item in "Pendings".
* In "Pendings," the seller can confirm or reject an order, with full details of the order and the delivery date requested by the buyer.
* Once the buyer confirms the delivery, the seller receives a notification and can archive the order.

Buyer Workflow:

* Create an account and select the desired product from the initial list to add it to the cart.
* Go to checkout to adjust quantities and choose a delivery date.
* After submitting the order, the user receives a notification and later another one depending on whether the seller confirms or cancels the order.
* Finally, the buyer can confirm receipt of an order to mark it as completed.

## Distinctiveness and Complexity

This application presented several challenges, tests, and the need for different approaches. **Bakery Store** stands out from a typical e-commerce platform because it operates as a marketplace (a single store with multiple sellers) and features a calendar system that is its main functionality and strongest point. Bakery Store is designed to simplify the management of small businesses or home-based ventures. It allows sellers to update prices based on the ingredients they use, organize their schedules, and manage orders received from buyers. At the same time, it enables them to showcase their products with a modern presentation and arrange their entire store according to their business capacities.

"I always try to practice new technologies with elaborate personal projects. Bakery Store is an idea I had in mind as a tool to help organize small home-based businesses, which are so common nowadays."

### Challenges

One of the most challenging aspects of this application was synchronizing date availability. A date’s availability depends on:

* Whether it’s a day disabled by the seller.
* Whether it’s a Sunday.
* Whether it’s after the highest "production time" of the products included in the order.
* Whether it complies with the seller’s daily production limit, considering both previous orders and the quantities of products in the current order.

Each order has its own delivery date, but the product quantities are not directly part of the order. These are calculated through the relationship between the "Order" and "ProductOrder" tables, which made it particularly challenging to calculate calendar availability. This required summing up the products in the cart along with those in pending orders.

Whenever the user adjusts quantities in the checkout, a request is sent to the server (via JavaScript) to update the available dates. The chosen date is then re-validated on the server side when the buyer completes their order to ensure it wasn’t altered before saving the new order in the database.

Another significant challenge was calculating product prices, as these values are dynamic and rely on the cost of the assigned ingredients. When creating a product, the user specifies its ingredients and their required quantities. The final product price is calculated as:

* Subtotal or labor cost.
* The cost of ingredients, divided by the quantity required for that product.

If the user updates the price of an ingredient (due to price increases or changes in purchase volume), this change affects the final price of all products that use that ingredient.

## Libraries

I’ve included the Flatpickr JavaScript library via CDN. It’s a useful tool for displaying a date picker that provides users with a convenient and visually appealing interface to select dates ([https://flatpickr.js.org/](https://flatpickr.js.org/)).

Both the code and styles of this library are used directly through the CDN, so no installation is required.

## Run application

The project uses Django with SQLite for the backend and Vanilla JavaScript with CSS for the frontend, requiring no specific setup. Updated versions of Python and Pip should be present on the machine:

* Create a virtual environment - `python3 -m venv venv`
* Activate the virtual environment - `source venv/bin/activate`
* Install dependencies - `pip install -r requirements.txt`
* Run migrations - `python3 manage.py migrate` (this step also generates the categories)
* Create a superuser - `python3 manage.py createsuperuser` (optional for accessing Django Admin)
* Run the development server - `python3 manage.py runserver`

## Issues

The application has a "known issue" with the implementation of the Flipkr library (JavaScript). This library has issues with Safari and iOS (this doesn't occur in Chrome and Firefox browsers, and the user experience is normal in those, as well as on Android). When testing with Safari, a noticeable error occurs that interrupts the execution of the code, preventing the application from displaying the "disabled days" whenever the user changes the "quantity" of products they want to order.

However, the backend checks the selected dates before storing the order, which allows the system to inform the user of the error and suggest using another browser to improve their experience. This error doesn't disrupt the buyer's flow, as they can complete the order correctly without selecting dates that should be disabled.

### Solutions

Despite trying different approaches, Safari and iOS continue to show the same error. The most viable solution is to switch the library for the date picker and integrate it using a module bundler like Webpack or similar.

## How I would continue this project

This project is at an advanced stage of development and, with some adjustments, could be ready for production. However, there are several areas for improvement or functionalities I'd like to integrate to make the application more complete and user-friendly:

* Replace the Flipkr library to fix "known issues."
* Add ratings and reviews for sellers.
* Implement internal messaging between buyers and sellers.
* Improve application security by integrating email verification and Captcha for account creation.
* Include payment options within the app (e.g., PayPal).
* Add a search feature for products and ingredients by name.
* Implement a favorites list.
* Change the app's name and categories to make it suitable for all types of products, not just food or baked goods.

## Explanation of Models/Entities

The application has 8 models/entities and 3 pivot models that facilitate the relationship between the entities.

- Order: It corresponds to each order placed.
  - buyer_user -> Buyer User (FK - User)
  - seller_user -> Seller User (FK - User)
  - total_amount -> Total amount of the order
  - delivery_date -> Delivery date of the order
  - created_at -> Creation date
  - deleted_at -> Deleted date (soft delete)
  - status -> Boolean to know the status of the order: Pending/Confirm
  - archived -> Boolean to know if the order is archived
  - token -> A unique token to identify the order
  - recived -> Boolean to know if the buyer receved the order
- OrderProduct: Pivot table between Order and Product, it also has other data.
  - product -> Product (FK - Product)
  - order -> Order (FK - Order)
  - quantity -> Quantity of the product in this order
  - created_at -> Creation date
  - deleted_at -> Deleted date (soft delete)
- Cart: The cart of the user.
  - user -> User (FK - User)
- CartProduct: Pivot table between Cart and Product, it also has other data.
  - product -> Product (FK - Product)
  - cart -> Cart (FK - Cart)
  - quantity -> Quantity of the product in this cart - It is not currently used in the code, but it could be useful for adding other features to the application. At the moment, the quantity is calculated directly in the checkout
  - created_at -> Creation date
- Category: It corresponds to the application categories, which are generated with a seeder (migration)
  - name -> Category name
  - image -> Category icon
  - created_at -> Creation date
- Ingredient: Every ingredient that are used to make the products
  - name -> Ingredient's name
  - description -> An optional description
  - price -> Price that is used to calculate the costs
  - size -> Size to calculate the costs per portion
  - measurement_user -> Unit to show in the view
  - availability -> Boolean to know if the product it's available or not - It is not currently used in the code, but it could be useful for adding other features to the application. At the moment, the ingredients can't be disabled
  - created_at -> Creation date
  - seller_user -> User that creates this ingredient (FK - User)
  - deleted_at -> Deleted date (soft delete) - It is not currently used in the code, but it could be useful for adding other features to the application. At the moment, the ingredients cannot be deleted
- Product: The products
  - name -> Product's name
  - subtotal_price -> Price without the price of ingredients
  - description -> Optional description
  - image -> URL to an image on internet
  - production_time -> Time that the seller needs to make/deliver the product
  - seller_user -> User (FK - User)
  - availability -> Boolean to know if the product it's available or not
  - created_at -> Creation date
  - cateogries -> Many to Many relationship (N:N - Category)
  - deleted_at -> Deleted date (soft delete) - It is not currently used in the code, but it could be useful for adding other features to the application. At the moment, the products cannot be deleted
- ProductIngredient: Pivot table between Product and Ingredient, it also has other data
  - product -> Product (FK - Product)
  - ingredient -> Ingredient (FK - Ingredient)
  - quantity -> Ingredient's quantity per product
  - created_at -> Creation date
  - deleted_at -> Deleted date (soft delete) - It is not currently used in the code, but it could be useful for adding other features to the application. At the moment, they are configured with 'ON DELETE CASCADE'
- User: Users, inherits from AbstracUser
  - max_prod_capacity -> User's maximum product per day
  - deleted_at -> Deleted date (soft delete) - It is not currently used in the code, but it could be useful for adding other features to the application. At the moment, the users cannot be deleted
- Notification: User's notifications
- - user -> User (FK - User)
  - notification_type -> There are a list with 3 possible types
  - message -> Notification's text
  - is_read -> Notification's status
  - created_at -> Creation date

## File listing

This project has multiple applications: Dashboard, which contains the logic for managing the seller panel and most of its views; Orders, which holds the code related to orders; Products, for product logic; and finally, Users, which handles user authentication and notifications.

Within the main application "Bakery Store," all assets (images, JS, and CSS for the entire project) and views (templates) are stored. Folder structure:

```
|- devenv -> Enviroment
|- bakery_store
	|- static
		|- img -> Images and SVGs of the project
		|- js
			|- app.js -> Logic about Cart, Notifications and Format Prices
			|- changeAbilability.js -> Product Abailability Logic
			|- checkout.js -> Calendar logic (library Flatpickr), quantity and prices calculates
			|- deliveries.js -> Logic to change the order's status
			|- newProduct.js -> Logic of the Product form, ingredient adding and total price calculate
			|- orders.jsp -> Dashboard pending orders
			|- settings.js -> Calendar logic to set days off
		|- styles
			|- app.css -> All the styles of the project
	|- templates
		|- auth
			|- login.html
			|- register.html
		|- dashboard
			|- create_ingredient.html
			|- create_product.html
			|- edit_ingredient.html
			|- edit_product.html
			|- index.html
			|- ingredients.html
			|- ingredients.html
			|- products.html
			|- settings.html
		|- home
			|- index.html
			|- show_product.html
		|- layouts
			|- dashboard.html
			|- layout.html
		|- orders
			|- archived_deliveries.html
			|- archived.html
			|- checkout.html
			|- pending_deliveries.html
			|- pendings.html
	|- context_processors.py -> A context processor to have the actual date's variable available in all the views.
|- dashboard
	|- urls.py -> Seller Panel views and API routes (check calendar availability).
	|- views.py - Routes Controllers.
|- orders
	|- models.py -> Order, OrderProduct (pivot), Cart and CartProduct (pivot) models.
	|- urls.py -> Checkout and Pending views. Also the API routes for Cart and Order CRUD.
	|- views.py - Routes Controllers.
	|- utils.py -> Helper to generate a token (Unique ID) for the orders.
|- products
	|- models.py -> Category, Ingredient, Product and ProductIngredient (pivot) models.
	|- urls.py -> Public and Dashboard URLs for Products and Ingredients. Also the API routes for Product availability.
	|- views.py - Routes Controllers.
|- users
	|- models.py -> User, SellerTimeOff and Notification models.
	|- urls.py -> Authentication and Notification routes.
	|- views.py - Routes Controllers.
```
