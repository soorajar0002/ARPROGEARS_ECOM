# AR PROGEARS
AR PROGEARS is a ecommerce website build using HTML, CSS, Bootstrap as frontend and Django as backend. It is a completely functional website with all the standard features such as product view, add to cart, single page product view, offers, coupon code and order management.
## Features

* User and Admin Dashboard
* View Products and its detailed view
* Payment Integration
* Order Management 
* User Management
* Product Management
* OTP verification using Twilio

## Screenshots

![Home](https://soorajar.cf/static/media/arprogears.3125a856deccdd173427.jpg)

## Prerequisites

* Django 3.1+
* Python 3.7+
* Other dependencies are listed in `requirements.txt`


## Installation

1. Clone this repository
2. Create a virtual environment and activate it
3. Install the dependencies: `pip install -r requirements.txt`
4. Run the migrations: `python manage.py migrate`
5. Collect the static files: `python manage.py collectstatic`
6. Start the development server: `python manage.py runserver`

## Usage

1. Visit http://localhost:8000 to view the website
2. If you want to access the admin dashboard, create a admin account and log in

## Deployment

To deploy this project, you can use AWS EC2 instance. Use WSGI server such as Gunicorn and Nginx to deploy the site.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License.

