from rest_framework_simplejwt.tokens import RefreshToken

class CashierToken(RefreshToken):
    """Custom token for cashiers with role claim"""
    
    @classmethod
    def for_cashier(cls, cashier):
        token = cls()
        token['cashier_id'] = str(cashier.id)
        token['restaurant_id'] = str(cashier.restaurant.id)
        token['role'] = 'cashier'
        token['name'] = cashier.name
        return token
