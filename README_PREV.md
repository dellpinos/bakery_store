# BakeryStore

Esta aplicación es un marketplace donde los usuarios pueden ordenar comidas/platos artesanales, al mismo tiempo pueden acceder a un "Seller Panel" donde crear y ofrecer sus propios productos. Esta aplicación está orientada a los emprendimientos caseros de comida pero podria ampliarse a otros rubros.

Al acceder al dashboard, un usuario puede crear sus propios *productos*. Para que el calculo de precios sea dinámico y se adapte a todo tipo de insumos (diferentes precios por cantidad o tamaño), el usuario también puede crear *ingredientes* que estarán disponibles para seleccionarlos como parte de cada producto.
Los nuevos productos cuentan con un "tiempo de producción" ya que puede cambiar dependiendo del articulo y de la capacidad del vendedor, también con un precio base para incluir la "mano de obra" o los insumos que no están siendo calculados dentro de los ingredientes. El precio final del producto es calculado como la suma del precio base más la cantidad utilizada de cada ingrediente.

Dentro del dashboard el usuario también puede acceder a "Settings" donde configura la cantidad máxima de productos que puede entregar/preparar por dia, este número es variable ya que no todos los usuarios tienen la misma capacidad de producción. Al mismo tiempo el usuario puede seleccionar "days off" que son días deshabilitados en su calendario, de esta forma puede programar vacasiones o dias libres. También cuenta con un botón para deshabilitar todos los productos publicados siempre y cuando estos productos no sean parte de ordenes pendientes.

Otra opción del dashboard es "Pendings" que es la vista donde se listan todas las ordenes pendientes, aquí el usuario puede confirmar o cancelar las ordenes. Una vez confirmadas, el comprador puede cambiar su status a "entregadas" y luego el vendedor puede archivar estas ordenes para ambos. Las ordenes archivadas siguen visibles para me ambos usuarios pero no son tomadas en cuenta en el calendario del vendedor.

El usuario comprador accede al listado completo de productos en la aplicación, puede utilizar las "categorias" como filtros para facilitar la busqueda. Una vez que accede a un producto y decide comprarlo este es agregado al Carrito, el usuario puede seleccionar todos los productos que quiera de un mismo vendedor siempre y cuando no supere el máximo de producción diaria de este vendedor.
En el Checkout, el usuario puede cambiar las cantidades de cada producto (siempre teniendo en cuenta el máximo de producción del vendedor) y seleccionar una fecha de entrega. Las fechas seleccionables son aquellas que no hayan sido deshabilitadas por el vendedor, y que no superen el "maximo de producción diaria" de esste vendendor.

Una vez finalizada la orden el comprador y el vendedor son notificados. Cuando el vendedor acepte esta orden, el comprador puede cambiar su status a "entregada" para dar por finalizado el pedido. Posteriormente el vendedor también puede archivar la orden para que esté disponible en "Archived Deliveries".

## Flujos

Flujo del Vendedor:

- Crear cuenta y acceder a "Seller Panel".
- Crear uno o más "Ingredientes" con su precio y cantidad por bulto (la cantidad sirve para calcular el valor fraccionado).
- Crear producto con precio base, ingredientes y tiempo de producción.
- Opcional: configurar "days off" y/o producción diaria máxima.
- Cuando un comprador hace un pedido el vendedor recibe una notificación y un nuevo elemento en "Pendings".
- Dentro de "Pendings" puede confirmar o rechazar un pedido, aquí cuenta con toda la información sobre la orden y la fecha de entrega solicitada por el comprador.
- Una vez que el comprador confirma la entrega, el vendedor recibe una nueva notificación y puede archivar la orden.

Flujo del Comprador

- Crear cuenta y seleccionar el producto deseado en el listado inicial para añadirlo al carrito.
- Acceder al checkout donde se pueden cambiar las cantidades y seleccionar una fecha.
- Una vez enviada la orden, el usuario recibe una notificación y luego otra dependiendo si el vendedor confirma o cancela la orden.
- Finalmente el comprador puede confirmar la recepción de un pedido y de essta forma darlo por finalizado.

## Distinctiveness and Complexity

Esta aplicación supuso varios desafios, pruebas y la necesidad de diferentes enfoques. Bakery Store se diferencia de un e-commerce principalmente porque funciona como un marketplace (una sola tienda con multiples vendedores), pero también cuenta con un sistema de calendario que es la funcionalidad principal y el punto fuerte de la aplicación. Bakery Store esta diseñado para facilitar la organización de un emprendimiento o un negocio perqueño, permite al vendedor actualizar los precios en base a los insumos que utiliza, organizar su agenda y también las ordenes recibidas por los compradores. Al mismo tiempo puede publicar sus productos con una presentación moderna y organizar toda su tienda acorde a las capacidades de su negocio.

"Siempre intento prácticar las nuevas tecnologias con proyectos personales elaborados, BakeryStore es una idea que tenia en mente como un organizador para los pequeños emprendimientos caseros que son tan comunes hoy en dia."

## Retos

Uno de los retos más díficiles de esta aplicación fue la sincronización en la disponibilidad de fechas, que una fecha se encuentre disponible depende de:

- Si es un día deshabilitado por el vendedor.
- Si es domingo.
- Si es despúes del "production time" más alto de los productos que conforman la orden.
- Si cumple con la producción diaria máxima del vendedor, esto tiene en cuenta ordenes anteriores y cantidades de productos en la orden actual.

Cada orden tiene su propia fecha de entrega pero la cantidad de productos no es parte de la orden, estos se calculan mediante la relación entre las tablas "Order" y "ProductOrder" por lo cual ha sido todo un desafio calcular la disponibilidad del calendario haciendo la suma de los productos en el carrito y los productos dentro de las ordenes pendientes.

Cada vez que el usuario cambia las cantidades en el Checkout se envia un request al servidor (mediante Js) para volver a consultar los dias disponibles. La fecha escogida vuelve a ser comprobada desde el servidor una vez que el comprador finaliza su orden, este dato podría ser alterado y es necesario validarlo antes de almacenar la nueva orden en la base de datos.

Otro reto reelevante fue el calculo de los precios de los productos, este valor es dinámico ya que utiliza el valor de los ingredientes que se le asignan. Al crear un producto el usuario indica los ingredientes y la cantidad de los mismos, el producto final es el resultado de:

- Subtotal o precio de mano de obra
- Precio de los ingredientes dividido por la cantidad necesaria en este producto.

Si el usuario cambia el valor de un ingrediente (ya sea por aumentos o cambios en el volumen de compra), este valor afecta al precio final de todos los productos que lo utilicen.

## Librerias

Mediante CDN he incorporado la libreria Flatpickr de JavaScript, es útil para mostrar un date picker que permita al usuario escoger fechas con una interfaz adecuada (https://flatpickr.js.org/).

Tanto el código como los estilos de esta libreria se utilizan mediante CDN, no es necesario ningún tipo de instalación.

## Pasos para ejecutar el proyecto

El proyecto utiliza Django con SQLite en el backend y Vanilla Javascript con CSS en el frontend, no requiere una configuración especifica. Python y Pip deben estar presentes en la máquina:

- Crear VE - `python3 -m venv venv`
- Activar VE - `source venv/bin/activate`
- Instalar dependencias - `pip install -r requirements.txt`
- Ejecutar migraciones - `python3 manage.py migrate` (este paso también genera las categorias)
- Crear superusuario - `python3 manage.py createsuperuser` (opcional para acceder a Django Admin)
- Ejecutar servidor de desarrollo - `python3 manage.py runserver`

## Issues

La apliación tiene un "issue conocido" en la implementación de la libreria Flipkr (JavaScript), esta libreria tiene problemas con Safari únicamente (en los navegadores Chrome y Firefox esto no ocurre y el usuario tiene un flujo de navegación normal). Al hacer pruebas con Safari es evidente un error que interrumpe la ejecución del código, esto impide a la aplicación mostrar los "disabled days" cada vez que cambia la "cantidad" de productos que desea ordenar.

De todas formas el backend comprueba las fechas escogidas por el usuario antes de almacenar la orden, esto permite informar el error al usuario y sugerirle el uso de otro navegador para mejorar su experiencia. Este error no impide el flujo de navegación del comprador ya que puede concretar la orden correctamente y sin escoger fechas que deberian estar deshabilitadas.

### Posibles soluciones

A pesar de probar diferentes enfoques Safari sigue dando el mismo error, la solución más viable es cambiar la libreria para el date picker e integrarla mediante un module bundler como Webpack o similar.

## Como continuaria este proyecto

Este proyecto tiene un desarrollo avanzado y con ciertos ajustes podría estar listo para producción, de todas formas hay varios puntos a mejorar o funcionalidades que me gustaría integrar para obtener una aplicación más completa y viable para los usuarios:

- Agregar calificaciones y comentarios sobre los vendedores.
- Agregar mensajeria interna entre comprador y vendedor.
- Mejorar la seguridad de la aplicación integrando verificación por email y Captcha para la creación de cuentas.
- Incluir cobros en la aplicación (Paypal, por ejemplo).
- Agregar un buscador por nombre de productos e ingredientes.
- Agregar listado de favoritos.
- Cambiar el nombre de la aplicación y las categorias con el fin de que pueda ser utilizada para todo tipo de productos, no solo alimentos o pasteleria.

## Explicación de Modelos/Entidades

La aplicación cuenta con 8 modelos/entidades y 3 modelos/pivote que facilitan la relación entre las entidades.

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

## Listado de archivos

Este proyecto cuenta con multiples aplicaciones: Dashboard donde se encuentra la lógica para el manejo del panel de vendedor y la mayoria de sus vistas, Orders donde se encuentra el código correspondiente a las ordenes, Products para la lógica de los productos y por último Users donde se maneja la autenticación del usuario y la notificación.

Dentro de la aplicación principal "Bakery Store" se encuentran todos los assets (imagenes, Js y CSS de todo el proyecto) y las vistas (templates). Estructura de carpetas:



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
