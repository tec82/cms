base_url = "https://api.abacatepay.com/v2/"

def make_custumer(request,user,cpf):   

    customer_url = base_url + "customers/create"

    customer_payload = {
        "name": user.name,
        "email": user.email,
        "taxId": cpf
    }

    print(customer_payload)

    '''
    headers = {
        "Authorization": "Bearer abc_dev_hNHFxMcAKu4JjwgfQeeF62fJ",
        "Content-Type": "application/json"
    }

    response = requests.post(customer_url, json=customer_payload, headers=headers)
    print(response.json())'''
