# Flask URL Shortener

This is a simple URL shortener built with Flask, SQLAlchemy, and MySQL. It allows users to shorten URLs, track access logs, and set expiration times for shortened links. Users can also add password protection to the shortened URLs.

## Features

- **Shorten URLs**: Generate a short URL from a long URL.
- **Password Protection**: Optionally protect shortened URLs with a password.
- **Expiration Time**: Set an expiration time (in hours) for shortened URLs.
- **Access Logs**: Track the number of visits and IP addresses of users accessing the shortened URL.
- **Analytics**: View the analytics of each shortened URL, including visit count and access logs.

## Requirements

- Python 3.11
- MySQL (for database)

### Dependencies

You can install the required dependencies by running:

```bash
pip install -r requirements.txt



### Installation
1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd url_shortener

2. Run the application:

  ```bash
  python app.py

3. Open your browser and visit:

  ```arduino
   http://127.0.0.1:5000
