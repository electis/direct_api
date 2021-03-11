def check_auth(body: ByteString, outer_sign: str):
    inner_sign = create_signature(settings.SECRET_TOKEN.encode(), body)

    return hmac.compare_digest(outer_sign, inner_sign)
