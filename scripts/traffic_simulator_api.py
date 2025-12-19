#!/usr/bin/env python3
"""
Coveo Commerce API Traffic Simulator

Generates realistic ecommerce traffic by making actual API calls to:
- Coveo Commerce Search API (for search queries)
- Coveo Commerce Listing API (for product listing pages)
- Coveo Analytics Event Protocol (for commerce events)

Auto-discovers PLP pages and scales automatically as you add new ones.
Uses industry-standard conversion rates for realistic user behavior simulation.
"""

import json
import random
import time
import uuid
import os
import argparse
import re
import glob
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote
from dotenv import load_dotenv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

# Load environment variables
load_dotenv()


class PLPParser(HTMLParser):
    """Extract brand filters from PLP HTML files"""
    
    def __init__(self):
        super().__init__()
        self.brand_filter = None
        self.view_url = None
        self.in_script = False
        self.script_content = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.in_script = True
            self.script_content = ""
    
    def handle_data(self, data):
        if self.in_script:
            self.script_content += data
    
    def handle_endtag(self, tag):
        if tag == 'script' and self.in_script:
            self.in_script = False
            # Extract brand filter: cq: '@ec_brand=="Nike"'
            match = re.search(r"cq:\s*'@ec_brand==\"([^\"]+)\"'", self.script_content)
            if match:
                self.brand_filter = match.group(1)
            
            # Extract view URL: view: {url: '/brand/nike'}
            match = re.search(r"view:\s*\{url:\s*'([^']+)'", self.script_content)
            if match:
                self.view_url = match.group(1)


class CoveoCommerceAPISimulator:
    """
    Simulates realistic ecommerce traffic using actual Coveo Commerce API calls.
    
    Industry benchmark conversion rates:
    - 47% bounce rate
    - 35% search click-through rate
    - 9% add-to-cart rate
    - 2.5% purchase conversion (accounting for 69.8% cart abandonment)
    """
    
    # Industry benchmark conversion rates (increased for more data)
    BOUNCE_RATE = 0.47
    SEARCH_RATE = 0.65
    BROWSE_RATE = 0.35
    SEARCH_CLICK_RATE = 0.35
    BROWSE_CLICK_RATE = 0.25
    ADD_TO_CART_RATE = 0.18  # Increased from 0.09
    CART_ABANDONMENT_RATE = 0.50  # Reduced from 0.698
    AVG_PRODUCTS_VIEWED = 3.2
    AVG_ITEMS_IN_CART = 2.1
    AVG_SEARCHES_PER_SESSION = 1.8
    
    def __init__(self, verbose: bool = False, dry_run: bool = False, max_workers: int = 10):
        """Initialize the simulator with optional parallel execution"""
        self.verbose = verbose
        self.dry_run = dry_run
        self.max_workers = max_workers
        
        # HTTP session for connection pooling (massive performance boost)
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=max_workers,
            pool_maxsize=max_workers * 2,
            max_retries=3
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        
        # Thread lock for stats updates
        self.stats_lock = Lock()
        
        # Coveo configuration
        self.access_token = os.getenv('COVEO_FRONTEND_ACCESS_TOKEN')
        self.org_id = os.getenv('COVEO_ORGANIZATION_ID', 'coveodocumentationtest')
        self.tracking_id = 'commerce-docs-demo'
        self.base_url = 'http://localhost:8080'
        
        # Commerce API endpoints
        self.platform_url = f"https://platform.cloud.coveo.com/rest/organizations/{self.org_id}"
        self.search_endpoint = f"{self.platform_url}/commerce/v2/search"
        self.listing_endpoint = f"{self.platform_url}/commerce/v2/listing"
        
        # Analytics Event Protocol endpoint - organization-specific
        self.analytics_endpoint = f"https://analytics.cloud.coveo.com/rest/organizations/{self.org_id}/events/v1"
        
        # Discover PLP pages
        self.plp_pages = self._discover_plp_pages()
        
        # Search query templates
        self.search_queries = [
            'shoes', 'running shoes', 'sneakers', 'boots', 'sandals',
            'bags', 'backpack', 'handbag', 'wallet', 'purse',
            'nike', 'adidas', 'under armour', 'steve madden',
            'mens', 'womens', 'kids', 'sale', 'new arrivals',
            'black', 'white', 'blue', 'red', 'waterproof'
        ]
        
        # Statistics (thread-safe updates via _increment_stat)
        self.stats = {
            'sessions': 0,
            'bounces': 0,
            'search_queries': 0,
            'search_api_calls': 0,
            'plp_visits': 0,
            'listing_api_calls': 0,
            'product_views': 0,
            'clicks': 0,
            'add_to_carts': 0,
            'purchases': 0,
            'total_revenue': 0,
            'analytics_events': 0
        }
    
    def _increment_stat(self, key: str, amount: float = 1):
        """Thread-safe stats increment"""
        with self.stats_lock:
            self.stats[key] += amount
    
    def _discover_plp_pages(self) -> List[Dict]:
        """Auto-discover and parse PLP pages from website/pages"""
        plp_pages = []
        
        for filepath in glob.glob('website/pages/simple-plp-*.html'):
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                parser = PLPParser()
                parser.feed(content)
                
                # Extract brand from filename if not found in HTML
                if parser.brand_filter or parser.view_url:
                    filename = os.path.basename(filepath)
                    brand_slug = filename.replace('simple-plp-', '').replace('.html', '')
                    
                    # Use brand from HTML or derive from filename
                    brand_name = parser.brand_filter or brand_slug.replace('-', ' ').title()
                    
                    plp_pages.append({
                        'file': filepath,
                        'brand': brand_name,
                        'brand_slug': brand_slug,
                        'view_url': parser.view_url or f'/brand/{brand_slug}',
                        'filter': f'@ec_brand=="{parser.brand_filter}"' if parser.brand_filter else None,
                        'url': f'http://localhost:8080/pages/{filename}'
                    })
                    
                    if self.verbose:
                        filter_info = f"filter: @ec_brand=\"{parser.brand_filter}\"" if parser.brand_filter else "no filter (uses listing config)"
                        print(f"   Found PLP: {brand_name} ({filter_info})")
            
            except Exception as e:
                if self.verbose:
                    print(f"   Warning: Could not parse {filepath}: {e}")
        
        if plp_pages and not self.verbose:
            print(f"✓ Discovered {len(plp_pages)} PLP page(s): {', '.join([p['brand'] for p in plp_pages])}")
            print(f"   Note: Only brands with listing configs will work (currently: Adidas)")
        
        return plp_pages
    
    def _make_search_request(self, query: str, client_id: str) -> Dict:
        """Make a Commerce API search request and return products with searchUid"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'url': 'https://sports-store.com/search',
            'query': query,
            'language': 'en',
            'country': 'CA',
            'currency': 'CAD',
            'trackingId': self.tracking_id,
            'clientId': client_id,
            'context': {
                'view': {
                    'url': 'https://sports-store.com/search'
                }
            }
        }
        
        if self.dry_run:
            if self.verbose:
                print(f"    [DRY RUN] Would search for: '{query}'")
            return {'products': [], 'totalCount': 0, 'searchUid': ''}
        
        try:
            response = self.session.post(self.search_endpoint, headers=headers, json=payload, timeout=10)
            
            if self.verbose and response.status_code != 200:
                print(f"    ⚠️  Search API error {response.status_code}: {response.text[:300]}")
            
            if response.status_code == 200:
                self._increment_stat('search_api_calls')
                data = response.json()
                products = data.get('products', [])
                response_id = data.get('responseId', '')
                
                # Log if responseId is missing
                if not response_id and self.verbose:
                    print(f"    ⚠️  Warning: Search API did not return a responseId!")
                
                # Send search event to analytics
                if response_id:
                    self._send_event_protocol('search', {
                        'url': 'https://sports-store.com/search',
                        'queryText': query,
                        'actionCause': 'searchboxSubmit',
                        'searchUid': response_id
                    }, client_id)
                
                return {
                    'results': products,
                    'totalCount': data.get('pagination', {}).get('totalCount', len(products)),
                    'searchUid': response_id
                }
            else:
                if self.verbose:
                    print(f"    Search API error: {response.status_code} - {response.text[:200]}")
                return {'results': [], 'totalCount': 0, 'searchUid': ''}
        
        except Exception as e:
            if self.verbose:
                print(f"    Search API exception: {e}")
            return {'results': [], 'totalCount': 0, 'searchUid': ''}
    
    def _make_listing_request(self, plp: Dict, client_id: str) -> Dict:
        """Make a Commerce API listing request for a PLP and return products with searchUid"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Ensure the URL is properly encoded (though it should already be clean)
        # The url field becomes analytics.documentLocation and must be a valid URI
        page_url = plp['url']  # Already a full URL like http://localhost:8080/pages/simple-plp-brand.html
        
        payload = {
            'url': page_url,
            'language': 'en',
            'country': 'CA',
            'currency': 'CAD',
            'trackingId': self.tracking_id,
            'clientId': client_id,
            'context': {
                'view': {
                    'url': plp['view_url']
                }
            }
        }
        
        # Add brand filter using cq parameter (only if PLP has explicit filter)
        if plp.get('filter'):
            payload['cq'] = plp['filter']
        
        if self.dry_run:
            if self.verbose:
                print(f"    [DRY RUN] Would load PLP: {plp['brand']}")
            return {'results': [], 'totalCount': 0, 'searchUid': ''}
        
        try:
            response = self.session.post(self.listing_endpoint, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                self._increment_stat('listing_api_calls')
                data = response.json()
                products = data.get('products', [])
                response_id = data.get('responseId', '')
                
                # Send search event to analytics for listing page view
                if response_id:
                    self._send_event_protocol('search', {
                        'url': plp['url'],
                        'queryText': '',  # Listings don't have query text
                        'actionCause': 'interfaceLoad',
                        'searchUid': response_id
                    }, client_id)
                
                return {
                    'results': products,
                    'totalCount': data.get('pagination', {}).get('totalCount', len(products)),
                    'searchUid': response_id
                }
            else:
                # Always log API errors
                print(f"\n⚠️  Listing API error: {response.status_code} - {response.text[:300]}")
                return {'results': [], 'totalCount': 0, 'searchUid': ''}
        
        except Exception as e:
            # Always log exceptions
            print(f"\n⚠️  Listing API exception: {e}")
            return {'results': [], 'totalCount': 0, 'searchUid': ''}
    
    def _send_event_protocol(self, event_type: str, event_data: Dict, client_id: str) -> bool:
        """
        Send commerce event using Coveo Event Protocol.
        
        Supports event types:
        - search: search event (for both search and listing API calls)
        - click: ec.productClick (product click with position and responseId)
        - view: ec.productView (product detail page view)
        - addToCart: ec.cartAction (add product to cart)
        - purchase: ec.purchase (completed transaction with revenue)
        """
        if self.dry_run:
            if self.verbose:
                print(f"    [DRY RUN] Would send {event_type} event")
            return True
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get current timestamp in milliseconds
            timestamp = int(time.time() * 1000)
            
            # Build Event Protocol payload as array
            events = []
            
            if event_type == 'search':
                # search event (for both search and listing API calls)
                event = {
                    'meta': {
                        'type': 'search',
                        'ts': timestamp,
                        'location': event_data.get('url', f'{self.base_url}/search'),
                        'referrer': None,
                        'config': {
                            'trackingId': self.tracking_id
                        },
                        'source': ['traffic-simulator@1.0.0'],
                        'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'clientId': client_id
                    },
                    'queryText': event_data.get('queryText', ''),
                    'actionCause': event_data.get('actionCause', 'searchboxSubmit'),
                    'responseId': event_data.get('searchUid', str(uuid.uuid4()))
                }
                events.append(event)
            
            elif event_type == 'click':
                # ec.productClick event
                # Validate responseId - must be a valid UUID from a recent search
                response_id = event_data.get('searchQueryUid', '')
                
                # Click events REQUIRE a valid responseId - if we don't have one, skip the click event
                # This prevents Coveo from silently dropping the event due to invalid responseId
                if not response_id:
                    if self.verbose:
                        print(f"    ⚠️  Skipping click event - no responseId available")
                    return False
                
                # Validate UUID format
                try:
                    uuid.UUID(response_id)
                except (ValueError, AttributeError):
                    if self.verbose:
                        print(f"    ⚠️  Skipping click event - invalid responseId format: {response_id}")
                    return False
                
                event = {
                    'meta': {
                        'type': 'ec.productClick',
                        'ts': timestamp,
                        'location': event_data.get('url', f'{self.base_url}/search'),
                        'referrer': None,
                        'config': {
                            'trackingId': self.tracking_id
                        },
                        'source': ['traffic-simulator@1.0.0'],
                        'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'clientId': client_id
                    },
                    'product': {
                        'productId': event_data['productData'].get('ec_item_id', ''),
                        'name': event_data['productData'].get('ec_name', ''),
                        'price': event_data['productData'].get('ec_price', 0)
                    },
                    'position': event_data.get('documentPosition', 1),
                    'responseId': response_id,
                    'currency': 'CAD'
                }
                events.append(event)
            
            elif event_type == 'view':
                # ec.productView event
                event = {
                    'meta': {
                        'type': 'ec.productView',
                        'ts': timestamp,
                        'location': f'{self.base_url}/product',
                        'referrer': None,
                        'config': {
                            'trackingId': self.tracking_id
                        },
                        'source': ['traffic-simulator@1.0.0'],
                        'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'clientId': client_id
                    },
                    'currency': 'CAD',
                    'product': {
                        'productId': event_data['productData'].get('ec_item_id', ''),
                        'name': event_data['productData'].get('ec_name', ''),
                        'price': event_data['productData'].get('ec_price', 0)
                    }
                }
                events.append(event)
            
            elif event_type == 'addToCart':
                # ec.cartAction event for add to cart
                event = {
                    'meta': {
                        'type': 'ec.cartAction',
                        'ts': timestamp,
                        'location': f'{self.base_url}/cart',
                        'referrer': None,
                        'config': {
                            'trackingId': self.tracking_id
                        },
                        'source': ['traffic-simulator@1.0.0'],
                        'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'clientId': client_id
                    },
                    'action': 'add',
                    'currency': 'CAD',
                    'product': {
                        'productId': event_data.get('ec_item_id', ''),
                        'name': event_data.get('ec_name', ''),
                        'price': event_data.get('ec_price', 0)
                    },
                    'quantity': event_data.get('ec_quantity', 1)
                }
                events.append(event)
            
            elif event_type == 'purchase':
                # ec.purchase event
                event = {
                    'meta': {
                        'type': 'ec.purchase',
                        'ts': timestamp,
                        'location': f'{self.base_url}/checkout/confirmation',
                        'referrer': None,
                        'config': {
                            'trackingId': self.tracking_id
                        },
                        'source': ['traffic-simulator@1.0.0'],
                        'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'clientId': client_id
                    },
                    'currency': 'CAD',
                    'products': [{
                        'product': {
                            'productId': event_data.get('ec_item_id', ''),
                            'name': event_data.get('ec_name', ''),
                            'price': event_data.get('ec_price', 0)
                        },
                        'quantity': event_data.get('ec_quantity', 1)
                    }],
                    'transaction': {
                        'id': f"TRX_{str(uuid.uuid4())[:8]}",
                        'revenue': event_data.get('ec_revenue', 0)
                    }
                }
                events.append(event)
            
            response = self.session.post(self.analytics_endpoint, headers=headers, json=events, timeout=5)
            
            if response.status_code in [200, 201, 204]:
                self._increment_stat('analytics_events')
                if self.verbose:
                    print(f"    ✓ {event_type} event sent successfully")
                return True
            else:
                if self.verbose:
                    print(f"    ⚠️ Event API error ({event_type}): {response.status_code} - {response.text[:200]}")
                return False
        
        except Exception as e:
            if self.verbose:
                print(f"    Event API exception ({event_type}): {e}")
            return False
    
    def simulate_bounce_session(self):
        """Simulate a bounced session"""
        if self.verbose:
            print("  Session: Bounce (no interaction)")
        self.stats['bounces'] += 1
    
    def simulate_search_session(self, client_id: str):
        """
        Simulate a search-driven session with real Commerce API calls.
        User performs 1-3 searches and may click on products and add to cart.
        """
        if self.verbose:
            print("  Session: Search & Browse")
        
        num_searches = max(1, int(random.gauss(self.AVG_SEARCHES_PER_SESSION, 0.5)))
        
        for _ in range(num_searches):
            query = random.choice(self.search_queries)
            self._increment_stat('search_queries')
            
            if self.verbose:
                print(f"    → Searching: '{query}'")
            
            # Make actual search API call
            results = self._make_search_request(query, client_id)
            total_results = results.get('totalCount', 0)
            products = results.get('results', [])
            search_uid = results.get('searchUid', '')
            
            if self.verbose:
                print(f"      Found {total_results} results")
            
            # Maybe click on results
            if products and random.random() < self.SEARCH_CLICK_RATE:
                num_clicks = min(int(random.gauss(self.AVG_PRODUCTS_VIEWED, 1)), len(products))
                
                for i in range(max(1, num_clicks)):
                    if i < len(products):
                        product = products[i]
                        self._simulate_product_interaction(product, client_id, from_search=True, 
                                                          query=query, search_uid=search_uid, position=i+1)
                        
                        # Maybe add to cart
                        if random.random() < self.ADD_TO_CART_RATE:
                            self._simulate_add_to_cart(product, client_id, search_uid)
                            return  # End session after add to cart
    
    def simulate_plp_browse_session(self, client_id: str):
        """
        Simulate browsing a Product Listing Page with real Commerce API call.
        User visits a random PLP and may click on products and add to cart.
        """
        if not self.plp_pages:
            return self.simulate_search_session(client_id)
        
        plp = random.choice(self.plp_pages)
        self._increment_stat('plp_visits')
        
        if self.verbose:
            print(f"  Session: Browse PLP - {plp['brand']}")
            print(f"    → Loading: {plp['url']}")
        
        # Make actual listing API call
        results = self._make_listing_request(plp, client_id)
        total_results = results.get('totalCount', 0)
        products = results.get('results', [])
        search_uid = results.get('searchUid', '')
        
        if self.verbose:
            print(f"      Found {total_results} {plp['brand']} products")
        
        # Maybe click on products
        if products and random.random() < self.BROWSE_CLICK_RATE:
            num_clicks = min(int(random.gauss(self.AVG_PRODUCTS_VIEWED, 1)), len(products))
            
            for i in range(max(1, num_clicks)):
                if i < len(products):
                    product = products[i]
                    self._simulate_product_interaction(product, client_id, from_search=False, 
                                                      search_uid=search_uid, position=i+1)
                    
                    # Maybe add to cart
                    if random.random() < self.ADD_TO_CART_RATE:
                        self._simulate_add_to_cart(product, client_id, search_uid)
                        return  # End session after add to cart
    
    def _simulate_product_interaction(self, product: Dict, client_id: str, 
                                     from_search: bool = False, query: str = None, search_uid: str = None, position: int = 1):
        """
        Simulate a user clicking on a product and viewing its details.
        Sends both ec.productClick and ec.productView events.
        """
        self._increment_stat('clicks')
        self._increment_stat('product_views')
        
        product_name = product.get('ec_name', product.get('title', 'Unknown'))
        product_brand = product.get('ec_brand', 'Unknown')
        product_uri = product.get('uri', product.get('clickUri', ''))
        product_id = product.get('ec_product_id', product.get('permanentid', ''))
        product_price = product.get('ec_price', 0)
        
        if self.verbose:
            source = f"search: '{query}'" if from_search else "listing"
            print(f"      → Clicked: {product_name} ({product_brand}) from {source}")
        
        # Send ec.productClick event
        # Properly encode the URL to ensure it's a valid URI
        if from_search and query:
            page_url = f'{self.base_url}/search?q={quote(query)}'
        else:
            page_url = f'{self.base_url}/listing'
        
        self._send_event_protocol('click', {
            'url': page_url,
            'productUrl': product_uri,
            'name': product_name,
            'documentPosition': position,
            'searchQueryUid': search_uid,
            'productData': {
                'ec_item_id': product_id,
                'ec_name': product_name,
                'ec_price': product_price,
                'ec_brand': product_brand
            }
        }, client_id)
        
        # Send ec.productView event
        self._send_event_protocol('view', {
            'productData': {
                'ec_item_id': product_id,
                'ec_name': product_name,
                'ec_price': product_price,
                'ec_brand': product_brand
            }
        }, client_id)
    
    def _simulate_add_to_cart(self, product: Dict, client_id: str, search_uid: str = ''):
        """
        Simulate adding a product to cart with potential purchase completion.
        Sends ec.cartAction event and possibly ec.purchase event based on cart abandonment rate.
        """
        self._increment_stat('add_to_carts')
        
        product_name = product.get('ec_name', product.get('title', 'Unknown'))
        price = product.get('ec_price', 0)
        product_id = product.get('ec_product_id', product.get('permanentid', ''))
        product_brand = product.get('ec_brand', 'Unknown')
        
        if self.verbose:
            print(f"      💰 Added to cart: {product_name}")
        
        # Send ec.cartAction event
        self._send_event_protocol('addToCart', {
            'ec_item_id': product_id,
            'ec_name': product_name,
            'ec_price': price,
            'ec_brand': product_brand,
            'ec_quantity': 1,
            'searchQueryUid': search_uid
        }, client_id)
        
        # Maybe complete purchase
        if random.random() > self.CART_ABANDONMENT_RATE:
            quantity = max(1, int(random.gauss(self.AVG_ITEMS_IN_CART, 0.7)))
            cart_total = price * quantity
            
            self._increment_stat('purchases')
            self._increment_stat('total_revenue', cart_total)
            
            if self.verbose:
                print(f"      ✓ PURCHASE: ${cart_total:.2f} CAD ({quantity} items)")
            
            # Send ec.purchase event
            self._send_event_protocol('purchase', {
                'ec_item_id': product_id,
                'ec_name': product_name,
                'ec_price': price,
                'ec_brand': product_brand,
                'ec_quantity': quantity,
                'ec_revenue': cart_total,
                'ec_currency': 'CAD',
                'searchQueryUid': search_uid
            }, client_id)
    
    def simulate_session(self):
        """
        Simulate a single user session with realistic behavior patterns.
        Session type is determined by industry benchmark rates (bounce, search, or browse).
        """
        self._increment_stat('sessions')
        client_id = str(uuid.uuid4())
        
        # Determine session type
        rand = random.random()
        
        if rand < self.BOUNCE_RATE:
            self.simulate_bounce_session()
        elif rand < self.BOUNCE_RATE + (self.SEARCH_RATE * (1 - self.BOUNCE_RATE)):
            self.simulate_search_session(client_id)
        else:
            self.simulate_plp_browse_session(client_id)
    
    def run(self, num_sessions: int):
        """Run the traffic simulator"""
        print(f"\n🚀 Starting Coveo Commerce API Traffic Simulator")
        print(f"   Simulating {num_sessions} user sessions with REAL API calls")
        print(f"   Organization: {self.org_id}")
        print(f"   Tracking ID: {self.tracking_id}")
        
        if self.dry_run:
            print(f"   ⚠️  DRY RUN MODE - No actual API calls will be made")
        print()
        
        if not self.access_token:
            print("⚠️  Warning: COVEO_FRONTEND_ACCESS_TOKEN not set")
            print("   Set it in .env file to make real API calls")
            self.dry_run = True
            print()
        
        start_time = time.time()
        
        if self.max_workers > 1 and not self.verbose:
            # Parallel execution for better performance
            print(f"   Using {self.max_workers} parallel workers\n")
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self.simulate_session) for _ in range(num_sessions)]
                
                completed = 0
                for future in as_completed(futures):
                    completed += 1
                    if completed % 10 == 0 or completed == num_sessions:
                        print(f"Progress: {completed}/{num_sessions} sessions", end='\r')
                    try:
                        future.result()
                    except Exception as e:
                        print(f"\n⚠️  Session error: {e}")
        else:
            # Sequential execution (for verbose mode or single worker)
            for i in range(num_sessions):
                if (i + 1) % 10 == 0 and not self.verbose:
                    print(f"Progress: {i + 1}/{num_sessions} sessions", end='\r')
                
                self.simulate_session()
        
        elapsed = time.time() - start_time
        
        # Print results
        print(f"\n\n✅ Simulation Complete!")
        print(f"   Duration: {elapsed:.1f} seconds")
        print(f"\n📊 Traffic Statistics:")
        print(f"\n   Total Sessions:     {self.stats['sessions']}")
        print(f"   Bounces:            {self.stats['bounces']} ({self.stats['bounces']/self.stats['sessions']*100:.1f}%)")
        print(f"\n   Search Queries:     {self.stats['search_queries']}")
        print(f"   Search API Calls:   {self.stats['search_api_calls']}")
        print(f"   PLP Visits:         {self.stats['plp_visits']}")
        print(f"   Listing API Calls:  {self.stats['listing_api_calls']}")
        print(f"\n   Product Clicks:     {self.stats['clicks']}")
        print(f"   Product Views:      {self.stats['product_views']}")
        print(f"   Add to Cart:        {self.stats['add_to_carts']} ({self.stats['add_to_carts']/max(self.stats['product_views'],1)*100:.1f}% of views)")
        print(f"   Purchases:          {self.stats['purchases']} ({self.stats['purchases']/self.stats['sessions']*100:.2f}% conversion)")
        print(f"\n   Total Revenue:      ${self.stats['total_revenue']:.2f} CAD")
        if self.stats['purchases'] > 0:
            print(f"   Avg Order Value:    ${self.stats['total_revenue']/self.stats['purchases']:.2f} CAD")
        print(f"\n   Analytics Events:   {self.stats['analytics_events']}")
        
        print(f"\n💡 This traffic is now visible in your Coveo dashboards!")
        print(f"   - Search Analytics: Shows queries, clicks, and CTR")
        print(f"   - Commerce Analytics: Shows views, add-to-cart, purchases")
        print(f"   - API Usage: Shows search and listing endpoint calls\n")


def main():
    parser = argparse.ArgumentParser(
        description='Generate real traffic using Coveo Commerce API calls',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (no actual API calls)
  python3 traffic_simulator_api.py --sessions 10 --dry-run --verbose
  
  # Generate realistic traffic (recommended starting point)
  python3 traffic_simulator_api.py --sessions 100
  
  # Large scale simulation with detailed logging
  python3 traffic_simulator_api.py --sessions 500 --verbose

Features:
  ✓ Auto-discovers PLP pages from website/pages/
  ✓ Makes real Commerce API calls (search & listing)
  ✓ Sends analytics events via Event Protocol
  ✓ Sends search events for proper click attribution
  ✓ Uses industry-standard conversion rates
  ✓ Scales automatically as you add new PLPs
  ✓ Tracks clicks, views, add-to-cart, and purchases
  ✓ All events visible in Coveo dashboards

Requirements:
  - COVEO_FRONTEND_ACCESS_TOKEN in .env file
  - COVEO_ORGANIZATION_ID in .env file (optional)
        """
    )
    
    parser.add_argument('--sessions', type=int, default=100,
                       help='Number of sessions to simulate (default: 100)')
    parser.add_argument('--workers', type=int, default=10,
                       help='Parallel workers for faster execution (default: 10, use 1 for sequential)')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed session activity')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate without making actual API calls')
    
    args = parser.parse_args()
    
    # Force sequential execution if verbose mode is enabled (cleaner output)
    max_workers = 1 if args.verbose else args.workers
    
    simulator = CoveoCommerceAPISimulator(verbose=args.verbose, dry_run=args.dry_run, max_workers=max_workers)
    simulator.run(args.sessions)


if __name__ == '__main__':
    main()
