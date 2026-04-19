from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Product
from django.contrib import messages

# LOGIN
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('product_list')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# PRODUCT LIST
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

# ADD PRODUCT (ADMIN ONLY)
@login_required
def add_product(request):
    if not request.user.is_staff:
        return redirect('product_list')

    if request.method == "POST":
        Product.objects.create(
            name=request.POST['name'],
            price=request.POST['price'],
            image=request.FILES['image']
        )
        return redirect('product_list')

    return render(request, 'store/product_form.html')

# CART
@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart
    return redirect('product_list')


@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * qty
            total += subtotal

            items.append({
                'product': product,
                'qty': qty,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            continue

    return render(request, 'store/cart.html', {
        'items': items,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1  
    else:
        cart[product_id] = 1    

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        if cart[product_id] > 1:
            cart[product_id] -= 1
        else:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')

@login_required
def update_product(request, product_id):
    if not request.user.is_staff:
        return redirect('product_list')

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.name = request.POST['name']
        product.price = request.POST['price']

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('product_list')

    return render(request, 'store/product_form.html', {'product': product})

@login_required
def delete_product(request, product_id):
    if not request.user.is_staff:
        return redirect('product_list')

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('product_list')
