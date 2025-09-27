import bcrypt

# 生成密码哈希
password = "123456"  # 替换为你的明文密码
salt_rounds = 12  # 加密强度，默认为12

# 生成盐并哈希密码
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=salt_rounds))
print(f"原始密码: {password}")
print("Hashed password:", hashed_password.decode('utf-8'))