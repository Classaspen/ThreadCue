ACTION_PATTERNS = [
    r"please send", r"please provide", r"could you send", r"can you send",
    r"need you to", r"please confirm", r"please complete", r"please review",
    r"please sign", r"please call",
]

QUOTE_WORDS = {"quote", "quotation", "estimate", "pricing", "price", "cost"}

DEFAULT_RULES = {
    "NEW_ENQUIRY": ["quote", "estimate", "pricing", "cost", "enquiry", "inquiry"],
    "PAYMENT": ["invoice", "payment", "overdue", "receipt"],
    "OFFER": ["offer", "make an offer", "purchase price"],
    "INSPECTION": ["inspection", "open home", "viewing"],
    "CONTRACT": ["contract", "section 32", "settlement", "exchange"],
    "APPRAISAL": ["appraisal", "valuation"],
}
