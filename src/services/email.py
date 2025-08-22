async def send_activation_email(email: str, token: str):
    print(
        f"[MOCK] Activation email to {email}: http://localhost:8000/users/activate/{token}"
    )


async def send_password_reset_email(email: str, token: str):
    print(
        f"[MOCK] Password reset email to {email}: http://localhost:8000/users/password-reset/{token}"
    )


async def send_order_confirmation_email(email: str, order_id: int):
    print(f"[Email] Send confirmation to {email} for order #{order_id}")
