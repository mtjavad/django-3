from django.shortcuts import render
from .models import Customer, Product, Order, OrderRow
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import re, json


@csrf_exempt
def product_store(request):
    if request.method=='POST':
        d = json.loads(request.body)
        code=d.get('code', '')
        name=d.get('name', '')
        price=d.get('price',-1)
        inventory=d.get('inventory', 0)
        # return JsonResponse({'id3': code}, status=201)

        if not code:
            msg={'message':'code is required'}
            return JsonResponse(msg, status=400)
        elif not name:
            msg={'message':'name is required'}
            return JsonResponse(msg, status=400)
        elif price==-1:
            msg={'message':'price is required'}
            return JsonResponse(msg, status=400)
        
        try:
            price=int(price)
            inventory=int(inventory)
            if price<0 or inventory<0:
                return JsonResponse({'message': 'price & inventory must positive'}, status=400)
            product = Product.objects.create(code=code, name=name, price=price, inventory=inventory)
            if product:
                return JsonResponse({'id': product.pk}, status=201)
        except ValueError:
            return JsonResponse({'message': 'price & inventory must integer'}, status=400)
        except IntegrityError:
            return JsonResponse({'message': 'Duplicate code'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only POST request is acceptable.'}, status=400)
    
@csrf_exempt
def product_index(request):
    if request.method=='GET':
        try:
            search=request.GET.get('search','')
            if not search:
                p=Product.objects.all()
                # return JsonResponse({ 'products' : list(p.values('id','code','name','price','inventory'))}, status=200)
            else:
                p= Product.objects.filter(name__contains=search)
                
            return JsonResponse({ 'products' : list(p.values('id','code','name','price','inventory'))}, status=200)
        except Exception as e:
                return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only GET request is acceptable.'}, status=400)


@csrf_exempt
def product_single(request, pk):
    if request.method=='GET':
        try:
            p=Product.objects.get(pk=pk)
            return JsonResponse({"id": p.id,"code": p.code,"name": p.name,"price": p.price,"inventory": p.inventory}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'message':'Product Not Found.'}, status=404)
        except Exception as e:
                return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only GET request is acceptable.'}, status=400)

@csrf_exempt
def product_update(request, pk):
    if request.method=='POST':
        try:
            p=Product.objects.get(pk=pk)
            d = json.loads(request.body)
            amount=int(d.get('amount', ''))
            if not isinstance(amount, int):
                return JsonResponse({'message':'amount must be integer'}, status=400)
            else:
                x=p.inventory-abs(amount)
                if amount<0 and x<0:
                    return JsonResponse({'message':'Not enough inventory.'}, status=400)
                elif amount>0:
                    p.increase_inventory(amount)  
                elif amount<0:
                    p.decrease_inventory(abs(amount))
                return JsonResponse({"id": p.id,"code": p.code,"name": p.name,"price": p.price,"inventory": p.inventory}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'message':'Product Not Found.'}, status=404)
        except ValueError:
            return JsonResponse({'message':'amount must be integer'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only POST request is acceptable.'}, status=400)


@csrf_exempt
def customer_register(request):
    if request.method=='POST':
        try:
            d = json.loads(request.body)
            username=d.get('username', '')
            password=d.get('password', '')
            first_name=d.get('first_name', '')
            last_name=d.get('last_name', '')
            email=d.get('email', '')
            phone=d.get('phone', '')
            address=d.get('address', '')

            if not username:
                msg={'message':'username is required'}
                return JsonResponse(msg, status=400)
            elif not password:
                msg={'message':'password is required'}
                return JsonResponse(msg, status=400)
            elif not first_name:
                msg={'message':'first_name is required'}
                return JsonResponse(msg, status=400)
            elif not last_name:
                msg={'message':'last_name is required'}
                return JsonResponse(msg, status=400)
            elif not email:
                msg={'message':'email is required'}
                return JsonResponse(msg, status=400)
            elif not phone:
                msg={'message':'phone is required'}
                return JsonResponse(msg, status=400)
            elif not address:
                msg={'message':'address is required'}
                return JsonResponse(msg, status=400)

            if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                return JsonResponse({'message': "email format not correct."}, status=400)

            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
            customer = Customer.objects.create(user=user, phone=phone, address=address)

            return JsonResponse({'id':customer.id}, status=201)

        # except IntegrityError:
        #     return JsonResponse({'message': 'Username already exists'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only POST request is acceptable.'}, status=400)


@csrf_exempt
def customer_index(request):
    if request.method=='GET':
        search=request.GET.get('search','')
        if not search:
            customers=Customer.objects.all()
        else:
            customers=Customer.objects.filter(Q(user__username__contains=search)|Q(user__first_name__contains=search)|Q(user__last_name__contains=search)|Q(address__contains=search))
            
        c=[{'id': customer.id,'username':customer.user.username,'first_name':customer.user.first_name,'last_name':customer.user.last_name,'email':customer.user.email,'phone':customer.phone,'address':customer.address,'balance':customer.balance} for customer in customers]
        return JsonResponse({ 'customers' : c}, status=200)
    else:
        return JsonResponse({'message': 'Only GET request is acceptable.'}, status=400)

def customer_single(request, pk):
    if request.method=='GET':
        try:
            customer=Customer.objects.get(pk=pk)
            return JsonResponse({'id': customer.id,'username':customer.user.username,'first_name':customer.user.first_name,'last_name':customer.user.last_name,'email':customer.user.email,'phone':customer.phone,'address':customer.address,'balance':customer.balance}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'message':'Customer Not Found.'}, status=404)
        except Exception as e:
                return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only GET request is acceptable.'}, status=400)

@csrf_exempt
def customer_update(request, pk):
    if request.method=='POST':
        try:
            customer=Customer.objects.get(pk=pk)
            user= customer.user
            username_old= user.username
            d = json.loads(request.body)
            id=d.get('id')
            username_new=d.get('username')
            password=d.get('password')
            first_name=d.get('first_name',user.first_name)
            last_name=d.get('last_name',user.last_name)
            email=d.get('email', user.email)
            phone=d.get('phone',customer.phone)
            address=d.get('address',customer.address)
            balance=int(d.get('balance', customer.balance))
            
            if balance<0:
                return JsonResponse({'message': 'balance should be positive integer'}, status=400)
            if email!=None and not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                return JsonResponse({'message': "email format not correct."}, status=400)

            if first_name!=None and first_name=='':
                msg={'message':'first_name is required'}
                return JsonResponse(msg, status=400)
            elif last_name!=None and last_name=='':
                msg={'message':'last_name is required'}
                return JsonResponse(msg, status=400)
            elif email!=None and email=='':
                msg={'message':'email is required'}
                return JsonResponse(msg, status=400)
            elif phone!=None and phone=='':
                msg={'message':'phone is required'}
                return JsonResponse(msg, status=400)
            elif address!=None and address=='':
                msg={'message':'address is required'}
                return JsonResponse(msg, status=400)

            user.last_name=last_name
            user.first_name=first_name
            user.email=email
            user.save()
            customer.user=user
            customer.phone=phone
            customer.address=address
            customer.balance=balance
            customer.save()           
            # return JsonResponse(customer)
            if username_new or password or id:
                return JsonResponse({'message': "Cannot edit customer's identity and credentials."}, status=403)            

            return JsonResponse({'id': customer.id,'username':customer.user.username,'first_name':customer.user.first_name,'last_name':customer.user.last_name,'email':customer.user.email,'phone':customer.phone,'address':customer.address,'balance':customer.balance}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({'message':'Customer Not Found.'}, status=404)
        except ValueError:
            return JsonResponse({'message': 'Balance should be integer.'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only POST request is acceptable.'}, status=400)

@csrf_exempt
def customer_login(request):
    if request.method=='POST':
        try:
            d = json.loads(request.body)
            username=d.get('username')
            password=d.get('password')
            
            if username==None:
                msg={'message':'username is required'}
                return JsonResponse(msg, status=400)
            elif password==None:
                msg={'message':'password is required'}
                return JsonResponse(msg, status=400)

            user = authenticate(request,username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'message': "You are logged in successfully."}, status=200)
            else:
                return JsonResponse({'message': "Username or Password is incorrect."}, status=404)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only POST request is acceptable.'}, status=400)

@csrf_exempt
def customer_logout(request):
    if request.method=='POST':
        # try:
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({'message': "You are logged out successfully."}, status=200)
        else:
            return JsonResponse({'message': "You are not logged in."}, status=403)
    else:
        return JsonResponse({'message': 'Only POST request is acceptable.'}, status=400)

@csrf_exempt
def customer_profile(request):
    if request.method=='GET':
        try:
            if request.user.is_authenticated:
                user=request.user
                customer=user.customer
                return JsonResponse({'id': customer.id,'username':user.username,'first_name':user.first_name,'last_name':user.last_name,'email':user.email,'phone':customer.phone,'address':customer.address,'balance':customer.balance}, status=200)
            else:
                return JsonResponse({'message': "You are not logged in."}, status=403)
        except Exception as e:
                return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only GET request is acceptable.'}, status=400)

@csrf_exempt
def cart_detail(request):
    if request.method=='GET':
        try:    
            if request.user.is_authenticated:
                user=request.user
                customer=user.customer
                order=Order.objects.filter(customer=customer,status=Order.STATUS_SHOPPING)
                # return JsonResponse({'items': list(order)}, status=200)
                if order:
                    order=order[0]
                    total_price=order.total_price
                    shops=OrderRow.objects.filter(order=order)
                    items=[{'code':shop.product.code,'name':shop.product.name,'price':shop.product.price,'amount':shop.amount} for shop in shops]
                    return JsonResponse({'total_price': total_price, 'items': items}, status=200)
                else:
                    items=[]
                    return JsonResponse({'items': items}, status=200)
                
            else:
                return JsonResponse({'message': "You are not logged in."}, status=403)
        except Exception as e:
                return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Only GET request is acceptable.'}, status=400)


@csrf_exempt
def cart_add_items(request):
    if request.method=='POST':
        if request.user.is_authenticated:
            user=request.user
            customer=user.customer
            d = json.loads(request.body)
            order=Order.initiate(customer)
            errors=[]

            for i in range(len(d)):
                try:
                    code=d[i].get('code','')
                    amount=d[i].get('amount',0)
                    product=Product.objects.filter(code=code)
                    if product:
                        product=product[0]
                        order.add_product(product=product, amount=amount)
                    else:
                        errors.append({'code':code, 'message':'Product not found.'})
                    
                except Exception as e:
                    errors.append({'code':code, 'message': str(e)})
            
            order2=Order.objects.filter(customer=customer,status=Order.STATUS_SHOPPING)
            if order2:
                order2=order2[0]
                total_price=order2.total_price
                shops=OrderRow.objects.filter(order=order2)
                items=[{'code':shop.product.code,'name':shop.product.name,'price':shop.product.price,'amount':shop.amount} for shop in shops]
                if not errors:
                    return JsonResponse({'total_price': total_price, 'items': items}, status=200)
                else:
                    return JsonResponse({'total_price': total_price, 'errors': errors, 'items': items}, status=400)

        else:
            return JsonResponse({'message': "You are not logged in."}, status=403)
    else:
        return JsonResponse({'message': 'Only POST request is acceptable.'}, status=400)


@csrf_exempt
def cart_remove_items(request):
    if request.method=='POST':
        if request.user.is_authenticated:
            user=request.user
            customer=user.customer
            d = json.loads(request.body)
            order=Order.initiate(customer)
            errors=[]
            for i in range(len(d)):
                try:
                    code=d[i].get('code','')
                    amount=d[i].get('amount','')
                    product=Product.objects.filter(code=code)
                    if product:
                        product=product[0]
                        if amount=='' or amount==None:
                            o= OrderRow.objects.filter(product=product, order=order)
                            if o:
                                amount=o[0].amount
                            else:
                                raise Exception('Product not found in cart.')

                        order.remove_product(product=product, amount=amount)
                    else:
                        errors.append({'code':code, 'message':'Product not found.'})
                    
                except Exception as e:
                    errors.append({'code':code, 'message': str(e)})
            
            order2=Order.objects.filter(customer=customer,status=Order.STATUS_SHOPPING)
            if order2:
                order2=order2[0]
                total_price=order2.total_price
                shops=OrderRow.objects.filter(order=order2)
                items=[{'code':shop.product.code,'name':shop.product.name,'price':shop.product.price,'amount':shop.amount} for shop in shops]
                if not errors:
                    return JsonResponse({'total_price': total_price, 'items': items}, status=200)
                else:
                    return JsonResponse({'total_price': total_price, 'errors': errors, 'items': items}, status=400)

        else:
            return JsonResponse({'message': "You are not logged in."}, status=403)
    else:
        return JsonResponse({'message': 'Only POST request is acceptable.'}, status=400)


@csrf_exempt
def cart_submit(request):
    if request.method=='POST':
        try:
            if request.user.is_authenticated:
                user=request.user
                customer=user.customer

                # order=Order.initiate(customer)
                order=Order.objects.filter(customer=customer,status=Order.STATUS_SHOPPING)
                if order:
                    order=order[0]                
                    order.submit()
                    shops=OrderRow.objects.filter(order=order)
                    total_price=order.total_price
                    items=[{'code':shop.product.code,'name':shop.product.name,'price':shop.product.price,'amount':shop.amount} for shop in shops]
                    return JsonResponse({'id':order.id, 'order_time':order.order_time, 'status': 'submitted', 'total_price': total_price, 'rows': items}, status=200)
                else:
                    return JsonResponse({'message': 'Not Found order with STATUS=SHOPPING to submit.'}, status=400)
            else:
                return JsonResponse({'message': "You are not logged in."}, status=403)

        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
            # return JsonResponse({'total_price': total_price, 'errors': errors, 'items': items}, status=400)
    else:
        return JsonResponse({'message': 'Only POST request is acceptable.'}, status=400)
