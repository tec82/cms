def subscribe():

    checkout_url = create_checkout(
        email=current_user.email,
        amount=1990
    )

    return redirect(checkout_url)




import requests

customer_url = "https://api.abacatepay.com/v2/customers/create"

customer_payload = {
    "name": "John Doe",
    "email": "johndoe@example.com",
    "taxId": "74778390091" # CPF or CNPJ if applicable
}

headers = {
    "Authorization": "Bearer abc_dev_hNHFxMcAKu4JjwgfQeeF62fJ",
    "Content-Type": "application/json"
}

response = requests.post(customer_url, json=customer_payload, headers=headers)
print(response.json())