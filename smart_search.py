def normalize(text):
    t = text.lower()
    if "साड़ी" in t or "sadi" in t:
        return "saree"
    if "mobile" in t or "मोबाइल" in t:
        return "gadgets"
    if "gift" in t or "गिफ्ट" in t:
        return "gift"
    return t
