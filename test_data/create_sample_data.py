"""
创建示例测试数据
"""
import pandas as pd
import os

# 创建目录
os.makedirs('test_data', exist_ok=True)

# 1. 客户反馈数据（用于情感分析）
feedback_data = pd.DataFrame({
    'customer_name': ['张三', '李四', '王五', '赵六', '钱七'],
    'feedback_text': [
        '产品质量非常好，物流也很快，非常满意！',
        '收到货发现包装破损，里面的产品也有划痕，要求退货！',
        '产品还行，没什么特别的。价格有点贵。',
        '客服态度很好，耐心解答问题，点赞！',
        '发货太慢了，等了两个星期才到，体验很差。'
    ],
    'feedback_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']
})

feedback_data.to_excel('test_data/customer_feedback.xlsx', index=False)
print("✓ 创建客户反馈数据: test_data/customer_feedback.xlsx")

# 2. 商品描述数据（用于文本处理）
product_data = pd.DataFrame({
    'product_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
    'product_name': [
        '苹果 iPhone 15 Pro Max',
        '戴尔XPS 13笔记本电脑',
        '索尼WH-1000XM5降噪耳机',
        '罗技MX Master 3S无线鼠标',
        '小米智能空气净化器Pro'
    ],
    'description': [
        'A17 Pro芯片，钛金属机身，6.7英寸超视网膜XDR显示屏',
        '13.4英寸全高清显示屏，第12代Intel酷睿i7处理器，16GB内存',
        '业界领先的降噪技术，30小时续航，支持LDAC高清音频',
        '人体工学设计，8000 DPI传感器，MagSpeed滚轮，支持多设备切换',
        'HEPA滤网，CADR值400m³/h，智能空气质量检测，米家APP控制'
    ],
    'price': [9999, 8999, 2499, 799, 1699]
})

product_data.to_excel('test_data/products.xlsx', index=False)
print("✓ 创建商品数据: test_data/products.xlsx")

# 3. 地址数据（用于结构化提取）
address_data = pd.DataFrame({
    'order_id': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005'],
    'address': [
        '北京市朝阳区建国路88号SOHO现代城',
        '上海市浦东新区世纪大道1000号',
        '广东省深圳市南山区科技园南区',
        '浙江省杭州市西湖区文三路100号',
        '四川省成都市武侯区天府大道中段1号'
    ]
})

address_data.to_excel('test_data/addresses.xlsx', index=False)
print("✓ 创建地址数据: test_data/addresses.xlsx")

# 4. 简单文本数据（用于通用测试）
simple_data = pd.DataFrame({
    'id': [1, 2, 3],
    'text': [
        '今天天气真好',
        '我喜欢编程',
        '人工智能很有趣'
    ]
})

simple_data.to_excel('test_data/simple_test.xlsx', index=False)
simple_data.to_csv('test_data/simple_test.csv', index=False, encoding='utf-8')
print("✓ 创建简单测试数据: test_data/simple_test.xlsx 和 test_data/simple_test.csv")

print("\n所有测试数据创建完成！")
