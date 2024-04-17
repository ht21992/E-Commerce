import json
import stripe

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from django.urls import reverse
from .models import Order, OrderItem
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound, JsonResponse


@login_required
@csrf_protect
def start_order(request):
    cart = Cart(request)
    data = json.loads(request.body)
    total_price = 0

    items = []

    for item in cart:
        product = item["product"]
        total_price += product.price * int(item["quantity"])

        items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product.name,
                    },
                    "unit_amount": product.price,
                },
                "quantity": item["quantity"],
            }
        )

    order = Order.objects.create(
        user=request.user,
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        phone=data["phone"],
        address=data["address"],
        zipcode=data["zipcode"],
        place=data["place"],
        paid=False,
        paid_amount=total_price,
    )
    stripe.api_key = settings.STRIPE_API_KEY_HIDDEN

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=items,
        mode="payment",
        success_url=request.build_absolute_uri(reverse("success"))
        + "?session_id={CHECKOUT_SESSION_ID}%s" % (f"&order_id={order.id}"),
        cancel_url=request.build_absolute_uri(reverse("failed"))
        + f"?order_id={order.id}",
    )

    payment_intent = session.payment_intent

    for item in cart:
        product = item["product"]
        quantity = int(item["quantity"])
        price = product.price * quantity

        item = OrderItem.objects.create(
            order=order, product=product, price=price, quantity=quantity
        )

    cart.clear()

    return JsonResponse({"session": session, "order": payment_intent})


@login_required
def success(request):
    try:
        session_id = request.GET.get("session_id")
        order_id = request.GET.get("order_id")
        if session_id is None:
            return HttpResponseNotFound()
        stripe.api_key = settings.STRIPE_API_KEY_HIDDEN
        session = stripe.checkout.Session.retrieve(session_id)
        current_order = ""
        if session.payment_status == "paid":
            current_order = get_object_or_404(Order, id=order_id)
            current_order.paid = True
            current_order.save()
        return render(request, "cart/success.html")
    except Exception as e:
        print(e)
        JsonResponse({"error": "Sth went wrong try again later"}, status=500)


@login_required
def failed(request):
    order_id = request.GET.get("order_id")
    order_id = request.GET.get("order_id")
    current_order = get_object_or_404(Order, id=order_id)
    current_order.delete()
    return render(request, "cart/failed.html")

