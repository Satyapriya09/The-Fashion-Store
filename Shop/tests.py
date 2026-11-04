import json
from datetime import date

from django.test import TestCase

from .models import Order, OrderUpdate, Product


class StorefrontTests(TestCase):
	def setUp(self):
		self.product = Product.objects.create(
			product_name='Everyday shirt',
			category="Men's Wear",
			sub_catgory='Shirts',
			price=125,
			product_description='A comfortable everyday shirt.',
			add_date=date.today(),
		)

	def test_root_displays_the_storefront(self):
		response = self.client.get('/')

		self.assertContains(response, 'Good style,')
		self.assertContains(response, self.product.product_name)

	def test_search_matches_product_names(self):
		response = self.client.get('/Shop/Search/', {'q': 'everyday shirt'})

		self.assertContains(response, self.product.product_name)

	def test_checkout_recalculates_total_and_product_details(self):
		response = self.client.post('/Shop/Checkout/', {
			'name': 'Customer Name',
			'email': 'customer@example.com',
			'address1': '1 Store Street',
			'address2': '',
			'city': 'London',
			'state': 'State',
			'zip_code': '12345',
			'phone': '1234567890',
			'itemsJson': json.dumps({f'pr{self.product.id}': [2, 'Forged product name', 1]}),
			'amount': '1',
		})

		self.assertContains(response, 'Your order is in.')
		order = Order.objects.get()
		saved_items = json.loads(order.items_json)
		self.assertEqual(order.amount, 250)
		self.assertEqual(saved_items[f'pr{self.product.id}'], [2, self.product.product_name, 125])
		self.assertEqual(OrderUpdate.objects.count(), 1)

	def test_checkout_rejects_products_missing_from_catalog(self):
		response = self.client.post('/Shop/Checkout/', {
			'name': 'Customer Name',
			'email': 'customer@example.com',
			'address1': '1 Store Street',
			'city': 'London',
			'state': 'State',
			'zip_code': '12345',
			'phone': '1234567890',
			'itemsJson': json.dumps({'pr999999': [1, 'Missing product', 1]}),
		})

		self.assertContains(response, 'could not be checked')
		self.assertEqual(Order.objects.count(), 0)

	def test_tracker_returns_order_status_and_items_as_json(self):
		order = Order.objects.create(
			items_json=json.dumps({f'pr{self.product.id}': [1, self.product.product_name, self.product.price]}),
			amount=self.product.price,
			name='Customer Name',
			email='customer@example.com',
			address='1 Store Street',
			city='London',
			state='State',
			zip_code='12345',
			phone='1234567890',
		)
		OrderUpdate.objects.create(order_id=order.order_id, update_desc='The order has been placed')

		response = self.client.post('/Shop/Track_Order/', {
			'orderId': str(order.order_id),
			'email': order.email,
		})

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()['found'])
		self.assertEqual(response.json()['items'][f'pr{self.product.id}'][1], self.product.product_name)
