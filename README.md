# ShopToolnix — Affiliate Store

## Quick Start

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Admin Panel
Go to `http://localhost:8000/admin/`
- Username: admin | Password: admin123 (change this!)

## Adding Products
1. Go to Admin → Products → Add Product
2. Fill in: Title, Description, Affiliate URL, Platform, Price
3. Set is_featured=True to show on homepage
4. Set is_deal_of_day=True for the Deal of the Day banner

## Deploying to shop.toolnix.pro
1. Set DEBUG=False in settings.py
2. Add `shop.toolnix.pro` to ALLOWED_HOSTS
3. Use gunicorn: `gunicorn config.wsgi`
4. Set up nginx to proxy port 8000

## Revenue Streams
- Affiliate links: replace `yourtag-20` with your Amazon tag
- AdSense: paste ad code in base.html inside the `<!-- ADS -->` comment
- Blog posts: add via Admin → Blog Posts

## Affiliate Programs to Join
- Amazon Associates: https://affiliate-program.amazon.com
- eBay Partner Network: https://partnernetwork.ebay.com
- ShareASale: https://www.shareasale.com
- CJ Affiliate: https://www.cj.com
