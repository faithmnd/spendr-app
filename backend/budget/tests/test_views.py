from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from budget.models import Wallet, Category, Transaction, BudgetGoal, RecurringBill
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()

class BudgetAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create initial test data
        self.wallet = Wallet.objects.create(
            user=self.user,
            name='Test Wallet',
            balance=1000.00,
            currency='PHP'
        )
        
        self.expense_category = Category.objects.create(
            user=self.user,
            name='Test Expense Category',
            description='Test Category Description',
            type='expense'
        )

        self.income_category = Category.objects.create(
            user=self.user,
            name='Test Income Category',
            description='Test Category Description',
            type='income'
        )

    # Wallet CRUD Tests
    def test_wallet_crud(self):
        # CREATE - Test POST wallet
        create_data = {
            'name': 'New Wallet',
            'balance': 500.00,
            'currency': 'PHP',
            'description': 'Test wallet description'
        }
        response = self.client.post(reverse('wallet-list-create'), create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], create_data['name'])
        wallet_id = response.data['id']

        # READ - Test GET single wallet
        response = self.client.get(reverse('wallet-detail', kwargs={'pk': wallet_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], create_data['name'])

        # READ - Test GET all wallets
        response = self.client.get(reverse('wallet-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Initial wallet + newly created one

        # UPDATE - Test PUT wallet
        update_data = {
            'name': 'Updated Wallet',
            'balance': 600.00,
            'currency': 'PHP',
            'description': 'Updated description'
        }
        response = self.client.put(
            reverse('wallet-detail', kwargs={'pk': wallet_id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], update_data['name'])

        # DELETE - Test DELETE wallet
        response = self.client.delete(reverse('wallet-detail', kwargs={'pk': wallet_id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        response = self.client.get(reverse('wallet-detail', kwargs={'pk': wallet_id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Category CRUD Tests
    def test_category_crud(self):
        # CREATE - Test POST category
        create_data = {
            'name': 'New Category',
            'description': 'Test category description',
            'type': 'expense'
        }
        response = self.client.post(reverse('category-list-create'), create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], create_data['name'])
        category_id = response.data['id']

        # READ - Test GET single category
        response = self.client.get(reverse('category-detail', kwargs={'pk': category_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], create_data['name'])

        # READ - Test GET all categories
        response = self.client.get(reverse('category-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Two initial categories + newly created one

        # UPDATE - Test PUT category
        update_data = {
            'name': 'Updated Category',
            'description': 'Updated description',
            'type': 'expense'
        }
        response = self.client.put(
            reverse('category-detail', kwargs={'pk': category_id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], update_data['name'])

        # DELETE - Test DELETE category
        response = self.client.delete(reverse('category-detail', kwargs={'pk': category_id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        response = self.client.get(reverse('category-detail', kwargs={'pk': category_id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Transaction CRUD Tests
    def test_transaction_crud(self):
        # CREATE - Test POST transaction
        create_data = {
            'wallet': self.wallet.id,
            'category': self.expense_category.id,
            'amount': 100.00,
            'transaction_type': 'expense',
            'description': 'Test Transaction',
            'date': date.today().isoformat()
        }
        response = self.client.post(reverse('transaction-list-create'), create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(response.data['amount']), create_data['amount'])
        transaction_id = response.data['id']

        # READ - Test GET single transaction
        response = self.client.get(reverse('transaction-detail', kwargs={'pk': transaction_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['amount']), create_data['amount'])

        # READ - Test GET all transactions
        response = self.client.get(reverse('transaction-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # UPDATE - Test PUT transaction
        update_data = {
            'wallet': self.wallet.id,
            'category': self.expense_category.id,
            'amount': 150.00,
            'transaction_type': 'expense',
            'description': 'Updated Transaction',
            'date': date.today().isoformat()
        }
        response = self.client.put(
            reverse('transaction-detail', kwargs={'pk': transaction_id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['amount']), update_data['amount'])

        # DELETE - Test DELETE transaction
        response = self.client.delete(reverse('transaction-detail', kwargs={'pk': transaction_id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        response = self.client.get(reverse('transaction-detail', kwargs={'pk': transaction_id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # BudgetGoal CRUD Tests
    def test_budget_goal_crud(self):
        # CREATE - Test POST budget goal
        create_data = {
            'category': self.expense_category.id,
            'amount': 500.00,
            'month': date.today().month,
            'year': date.today().year,
            'description': 'Test Budget Goal'
        }
        response = self.client.post(reverse('budgetgoal-list-create'), create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(response.data['amount']), create_data['amount'])
        budget_goal_id = response.data['id']

        # READ - Test GET single budget goal
        response = self.client.get(reverse('budgetgoal-detail', kwargs={'pk': budget_goal_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['amount']), create_data['amount'])

        # READ - Test GET all budget goals
        response = self.client.get(reverse('budgetgoal-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # UPDATE - Test PUT budget goal
        update_data = {
            'category': self.expense_category.id,
            'amount': 600.00,
            'month': date.today().month,
            'year': date.today().year,
            'description': 'Updated Budget Goal'
        }
        response = self.client.put(
            reverse('budgetgoal-detail', kwargs={'pk': budget_goal_id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['amount']), update_data['amount'])

        # DELETE - Test DELETE budget goal
        response = self.client.delete(reverse('budgetgoal-detail', kwargs={'pk': budget_goal_id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        response = self.client.get(reverse('budgetgoal-detail', kwargs={'pk': budget_goal_id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_dashboard_summary(self):
        url = reverse('dashboard-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_monthly_summary(self):
        url = reverse('monthly-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class BudgetAPIAuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Create a wallet for other_user
        self.other_user_wallet = Wallet.objects.create(
            user=self.other_user,
            name='Other User Wallet',
            balance=Decimal('1000.00'),
            currency='PHP'
        )

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access the API"""
        urls = [
            reverse('wallet-list-create'),
            reverse('category-list-create'),
            reverse('transaction-list-create'),
            reverse('budgetgoal-list-create'),
            reverse('dashboard-summary'),
            reverse('monthly-summary'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Django REST framework returns 403 for unauthenticated requests

    def test_other_user_data_access(self):
        """Test that users cannot access other users' data"""
        self.client.force_authenticate(user=self.user)
        
        # Try to access other user's wallet
        response = self.client.get(
            reverse('wallet-detail', kwargs={'pk': self.other_user_wallet.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class BudgetAPIValidationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.wallet = Wallet.objects.create(
            user=self.user,
            name='Test Wallet',
            balance=Decimal('1000.00'),
            currency='PHP'
        )
        
        self.expense_category = Category.objects.create(
            user=self.user,
            name='Test Expense Category',
            type='expense'
        )

    def test_invalid_wallet_creation(self):
        """Test wallet creation with invalid data"""
        # Test negative balance
        data = {
            'name': 'Invalid Wallet',
            'balance': '-100.00',
            'currency': 'PHP'
        }
        response = self.client.post(reverse('wallet-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid currency
        data['balance'] = '100.00'
        data['currency'] = 'INVALID'
        response = self.client.post(reverse('wallet-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_transaction_creation(self):
        """Test transaction creation with invalid data"""
        # Test future date
        future_date = (date.today() + timedelta(days=1)).isoformat()
        data = {
            'wallet': self.wallet.id,
            'category': self.expense_category.id,
            'amount': '100.00',
            'transaction_type': 'expense',
            'date': future_date
        }
        response = self.client.post(reverse('transaction-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test negative amount
        data['date'] = date.today().isoformat()
        data['amount'] = '-100.00'
        response = self.client.post(reverse('transaction-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class BudgetAPIFilterTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.wallet = Wallet.objects.create(
            user=self.user,
            name='Test Wallet',
            balance=Decimal('1000.00'),
            currency='PHP'
        )
        
        self.expense_category = Category.objects.create(
            user=self.user,
            name='Test Expense Category',
            type='expense'
        )

        # Create transactions with different dates
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.last_month = self.today.replace(day=1) - timedelta(days=1)

        self.transactions = [
            Transaction.objects.create(
                user=self.user,
                wallet=self.wallet,
                category=self.expense_category,
                amount=Decimal('100.00'),
                transaction_type='expense',
                date=self.today
            ),
            Transaction.objects.create(
                user=self.user,
                wallet=self.wallet,
                category=self.expense_category,
                amount=Decimal('200.00'),
                transaction_type='expense',
                date=self.yesterday
            ),
            Transaction.objects.create(
                user=self.user,
                wallet=self.wallet,
                category=self.expense_category,
                amount=Decimal('300.00'),
                transaction_type='expense',
                date=self.last_month
            )
        ]

    def test_transaction_date_filtering(self):
        """Test transaction filtering by date range"""
        url = reverse('transaction-list-create')
        
        # Test filtering for today's transactions
        response = self.client.get(f"{url}?start_date={self.today}&end_date={self.today}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filtering for this month's transactions
        start_of_month = self.today.replace(day=1).isoformat()
        response = self.client.get(f"{url}?start_date={start_of_month}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_transaction_category_filtering(self):
        """Test transaction filtering by category"""
        url = reverse('transaction-list-create')
        response = self.client.get(f"{url}?category_id={self.expense_category.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

class BudgetAPITransferTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.wallet1 = Wallet.objects.create(
            user=self.user,
            name='Wallet 1',
            balance=Decimal('1000.00'),
            currency='PHP'
        )
        
        self.wallet2 = Wallet.objects.create(
            user=self.user,
            name='Wallet 2',
            balance=Decimal('500.00'),
            currency='PHP'
        )

    def test_transfer_funds(self):
        """Test transferring funds between wallets"""
        url = reverse('transfer-funds')
        data = {
            'from_wallet': self.wallet1.id,
            'to_wallet': self.wallet2.id,
            'amount': '500.00',
            'description': 'Test transfer'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify wallet balances
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.assertEqual(self.wallet1.balance, Decimal('500.00'))
        self.assertEqual(self.wallet2.balance, Decimal('1000.00'))

        # Verify transfer transactions were created
        transactions = Transaction.objects.filter(description__contains='Test transfer')
        self.assertEqual(transactions.count(), 2)

    def test_invalid_transfer(self):
        """Test invalid transfer scenarios"""
        url = reverse('transfer-funds')
        
        # Test insufficient funds
        data = {
            'from_wallet': self.wallet1.id,
            'to_wallet': self.wallet2.id,
            'amount': '2000.00',
            'description': 'Invalid transfer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test transfer to same wallet
        data['amount'] = '100.00'
        data['to_wallet'] = self.wallet1.id
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 