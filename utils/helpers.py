def format_currency(amount: float) -> str:
    """Raqamni pul formatiga o'tkazish, masalan: 1 500 000 so'm"""
    try:
        val = int(round(amount))
        formatted = f"{val:,}".replace(",", " ")
        return f"{formatted} so'm"
    except Exception:
        return f"{amount} so'm"


def get_status_text(status: str) -> str:
    """Buyurtma holatini chiroyli ko'rsatish"""
    statuses = {
        "pending": "⏳ Kutilmoqda (Ko'rib chiqilmoqda)",
        "confirmed": "✅ Tasdiqlandi (Tayyorlanmoqda)",
        "shipping": "🚚 Yetkazib berish jarayonida",
        "completed": "🏁 Yetkazildi va yakunlandi",
        "cancelled": "❌ Bekor qilindi"
    }
    return statuses.get(status, status)
