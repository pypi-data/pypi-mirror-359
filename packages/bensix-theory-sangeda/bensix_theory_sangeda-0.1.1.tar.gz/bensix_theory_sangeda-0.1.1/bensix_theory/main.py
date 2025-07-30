def calculate_benzene_n(k):
    """
    计算苯的数量 N_苯(k) = (1/12)(k^6 + 3k^4 + 4k^3 + 2k^2 + 2k)

    参数:
        k: 正整数，通常表示某种变量或尺寸

    返回:
        N_苯(k) 的值
    """
    # 计算多项式的各部分
    k6 = k ** 6
    k4 = 3 * (k ** 4)
    k3 = 4 * (k ** 3)
    k2 = 2 * (k ** 2)
    k1 = 2 * k

    # 计算总和并除以12
    total = (k6 + k4 + k3 + k2 + k1) / 12.0
    return total

def demo():
    """演示函数，计算k=1到20的值"""
    for k in range(1, 21):
        result = calculate_benzene_n(k)
        print(f"当k={k}时，N_苯(k) = {result}")

if __name__ == "__main__":
    demo() 