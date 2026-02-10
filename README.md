# 🛞 GoWheels - Vehicle Rental Platform

A modern vehicle rental platform built with Django, featuring dark theme UI and comprehensive admin management.

## Features

- 🚗 Multi-category vehicle listings (Cars, Bikes, Trucks, Boats, Aerial, Electric)
- 🔐 Secure OTP-based authentication
- 👥 User & Seller dashboards
- 📱 Google OAuth integration
- 💰 Promotion & Sponsorship system
- 🎨 Modern dark theme UI with golden accents
- 📊 Super Admin panel for complete management
- 🔍 Advanced search & filtering

## Tech Stack

- **Backend:** Django 4.x, Python 3.x
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Authentication:** OTP (2Factor, Fast2SMS)
- **Deployment:** AWS EC2, Nginx, Gunicorn

## Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Gowheels.git
cd Gowheels

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Run server
python manage.py runserver
```

## Environment Variables

Create `.env` file:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=gowheels_new
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for AWS EC2 deployment guide.

## License

MIT License

## Contact

For support: info@gowheels.com
