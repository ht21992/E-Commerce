from django import template
from cart.cart import Cart
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_cart_icon(request, product_id):
    try:
        cart = Cart(request)

        if cart.get_item(product_id):
            return mark_safe(
                """<a
            href="#"
            hx-get="#"
            hx-target="#menu-cart-button"
            title="added to cart"
            hx-swap="outerHTML"
            class="text-cyan-500 hover:text-cyan-800 hx-purchase-btn cursor-help"
        >
            <svg xmlns="http://www.w3.org/2000/svg" fill="#009B77" stroke="#009B77" viewBox="0 0 24 24" width="24px" height="24px"><path d="M9 19.4L3.3 13.7 4.7 12.3 9 16.6 20.3 5.3 21.7 6.7z"/></svg>

        </a>"""
            )

        else:
            return mark_safe(
                f"""<a
            href="#"
            hx-get="/cart/add_to_cart/{product_id}"
            hx-target="#menu-cart-button"
            hx-swap="outerHTML"
            title="add to cart"
            class="text-cyan-500 hover:text-cyan-800 hx-purchase-btn"
        >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>

        </a>"""
            )

    except:
        return mark_safe("<small>Not Available</small>")
