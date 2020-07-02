from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    code = models.CharField(max_length=10, unique=True, error_messages={'unique':'Duplicate code', 'max_length': 'max_length limit is 10 char'})
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField(default=0)

    def increase_inventory(self, amount):
        if isinstance(amount, int) and amount>0:
            self.inventory=self.inventory+amount
            self.save()
        else:
            raise Exception('Amount must be positive integer. Please enter positive integer.')

    def decrease_inventory(self, amount):
        if isinstance(amount, int) and amount>0:
            self.inventory=self.inventory-amount
            if self.inventory<0:
                raise Exception('Not enough inventory for product {}.'.format(self.name))
            else:
                self.save()
        else:
            raise Exception('Amount must be positive integer. Please enter positive integer.')

    def __str__(self):
        return 'name= {}, inventory={}'.format(self.name, self.inventory)
    


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    balance = models.PositiveIntegerField(default=20000)

    def deposit(self, amount):
        if isinstance(amount, int) and amount>0:
            self.balance=self.balance+amount
            self.save()
        else:
            raise Exception('Amount must be positive integer. Please enter positive integer.')

    def spend(self, amount):
        if isinstance(amount, int) and amount>0:
            self.balance=self.balance-amount
            if self.balance<0:
                raise Exception('Not enough balance.')
            else:
                self.save()
        else:
            raise Exception('Amount must be positive integer. Please enter positive integer.')

    def __str__(self):
        return 'username= {}, balance= {}'.format(self.user.username, self.balance)
    


class OrderRow(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return 'product= {}, order= {}, amount= {}'.format(self.product, self.order, self.amount)
    

class Order(models.Model):
    # Status values. DO NOT EDIT
    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4
    
    ORDER_STATUS=(
        (STATUS_SHOPPING, 'در حال خرید'),
        (STATUS_SUBMITTED,'ثبت شده'),
        (STATUS_CANCELED,'لغو شده'),
        (STATUS_SENT,'ارسال شده')
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now_add=True)
    total_price = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=ORDER_STATUS, default=STATUS_SHOPPING)

    @staticmethod
    def initiate(customer):
        order = Order.objects.filter(customer=customer, status=Order.STATUS_SHOPPING)
        if order:
            return order[0]
        else:
            O = Order.objects.create(customer=customer)
            return O
           

    def add_product(self, product, amount):
        try:
            amount=int(amount)
        except ValueError:
            raise Exception('Amount must be positive integer. Please enter positive integer.')
        p=product
        if (not isinstance(amount, int)) or amount<0:
            raise Exception('Amount must be positive integer. Please enter positive integer.')
        if p.inventory < amount:
            raise Exception('Not enough inventory for product {}.'.format(p.name))
        elif amount==0:
            raise Exception('order amount should not be 0')
        else:
            o = OrderRow.objects.filter(product=product, order=self)
            if o: 
                o=o[0]
                o.amount=o.amount+amount
                o.save()
            else:
                OrderRow.objects.create(product=p, order=self, amount=amount)
            
            self.total_price=self.total_price+(amount*p.price)
            self.save()

    def remove_product(self, product, amount=None):
        o= OrderRow.objects.filter(product=product, order=self)
        if o:
            p=product
            o=o[0]
            if amount==None:
                self.total_price=self.total_price-(o.amount*p.price)
                self.save()
                o.delete()
            else:
                try:
                    amount=int(amount)
                except ValueError:
                    raise Exception('Amount must be positive integer. Please enter positive integer.')

                if (not isinstance(amount, int)) or amount<0:
                    raise Exception('Amount must be positive integer. Please enter positive integer.')
                o.amount=o.amount-amount
                if o.amount < 0:
                    raise Exception('Not enough product {} in order.'.format(o.product.name))
                self.total_price=self.total_price-(amount*p.price)
                self.save()
                if o.amount==0:
                    o.delete()
                else:
                    o.save()

        else:
            raise Exception('Product not found in cart.')

    def submit(self):
        # try:
        if self.status==self.STATUS_SHOPPING:
            s=self.customer
            if s.balance < self.total_price:
                raise Exception('Not enough money.')
            o_s=OrderRow.objects.filter(order=self.pk)

            for o in o_s:
                p=o.product
                m=o.amount
                if p.inventory < m:
                    raise Exception('Not enough inventory for product {}.'.format(p.name))
            
            for o in o_s:
                p=o.product
                m=o.amount 
                p.decrease_inventory(m)

            s.spend(self.total_price)
            self.status=self.STATUS_SUBMITTED
            self.save()
        else:
            raise Exception('only order with STATUS=SHOPPING can submit.')
       
    def cancel(self):
        if self.status==self.STATUS_SUBMITTED:
            o_s=OrderRow.objects.filter(order=self.pk)
            for o in o_s:
                p=o.product
                m=o.amount
                p.increase_inventory(m)

            s=self.customer
            s.deposit(self.total_price)
            self.status=self.STATUS_CANCELED
            self.save()
        else:
            raise Exception('only order with STATUS=SUBMITTED can cancel.')

    def send(self):
        if self.status==self.STATUS_SUBMITTED:
            self.status=self.STATUS_SENT
            self.save()
        else:
            raise Exception('only order with STATUS=SUBMITTED can send.')

    def __str__(self):
        return  'user= {}, total_price= {}, status= {} '.format(self.customer.user.username, self.total_price, self.status)
    