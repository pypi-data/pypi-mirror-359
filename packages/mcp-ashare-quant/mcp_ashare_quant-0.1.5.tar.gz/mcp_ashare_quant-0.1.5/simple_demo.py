#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Demo - 展示参数传递的核心逻辑
"""

import asyncio
from pydantic import BaseModel, Field
from typing import Optional, Annotated

# 模拟GetStockDataParams类
class GetStockDataParams(BaseModel):
    code: Annotated[str, Field(description="股票代码或中文名称")]
    frequency: Annotated[str, Field(default='1d', description="数据频率")]
    count: Annotated[int, Field(default=5, description="获取的数据条数")]
    end_date: Annotated[Optional[str], Field(default=None, description="结束日期")]

# 模拟get_stock_data函数
async def get_stock_data(code: str, frequency: str = '1d', count: int = 5, end_date: Optional[str] = None):
    """模拟获取股票数据的函数"""
    print(f"📊 调用get_stock_data函数:")
    print(f"  code: {code}")
    print(f"  frequency: {frequency}")
    print(f"  count: {count}")
    print(f"  end_date: {end_date}")
    
    # 模拟返回数据
    return [
        {"date": "2024-01-01", "open": 100.0, "high": 105.0, "low": 99.0, "close": 103.0},
        {"date": "2024-01-02", "open": 103.0, "high": 108.0, "low": 102.0, "close": 106.0},
        {"date": "2024-01-03", "open": 106.0, "high": 110.0, "low": 105.0, "close": 109.0},
    ]

async def demo_parameter_passing():
    """演示参数传递过程"""
    print("🚀 参数传递Demo")
    print("=" * 50)
    
    # 1. 模拟从外部接收的参数字典
    arguments = {
        "code": "贵州茅台",
        "frequency": "1d", 
        "count": 10,
        "end_date": "2024-12-01"
    }
    
    print("1️⃣ 原始参数字典:")
    for key, value in arguments.items():
        print(f"   {key}: {value}")
    
    print("\n2️⃣ 参数验证和转换:")
    # 这就是你问的那段代码的核心逻辑
    args = GetStockDataParams(**arguments)
    print(f"   ✓ 参数验证通过，创建了GetStockDataParams对象")
    print(f"   args.code: {args.code}")
    print(f"   args.frequency: {args.frequency}")
    print(f"   args.count: {args.count}")
    print(f"   args.end_date: {args.end_date}")
    
    print("\n3️⃣ 调用函数并传递参数:")
    # 这就是你问的那段代码
    result = await get_stock_data(
        code=args.code,
        frequency=args.frequency,
        count=args.count,
        end_date=args.end_date
    )
    
    print("\n4️⃣ 返回结果:")
    print(f"   获取到 {len(result)} 条数据")
    for i, item in enumerate(result):
        print(f"   [{i+1}] {item}")

async def demo_with_different_params():
    """演示不同参数组合"""
    print("\n" + "=" * 50)
    print("🔄 不同参数组合演示")
    print("=" * 50)
    
    test_cases = [
        # 最小参数
        {"code": "sh000001"},
        
        # 部分参数
        {"code": "sz000001", "count": 3},
        
        # 完整参数
        {"code": "贵州茅台", "frequency": "1w", "count": 8, "end_date": "2024-11-30"},
        
        # 使用默认值
        {"code": "比亚迪", "frequency": "1d", "count": 5, "end_date": None}
    ]
    
    for i, arguments in enumerate(test_cases, 1):
        print(f"\n📋 测试案例 {i}:")
        print(f"   输入参数: {arguments}")
        
        # 参数验证和转换
        args = GetStockDataParams(**arguments)
        
        # 显示实际传递的参数
        print(f"   实际传递:")
        print(f"     code={args.code}")
        print(f"     frequency={args.frequency}")
        print(f"     count={args.count}")
        print(f"     end_date={args.end_date}")
        
        # 模拟调用
        result = await get_stock_data(
            code=args.code,
            frequency=args.frequency,
            count=args.count,
            end_date=args.end_date
        )
        print(f"   ✓ 成功获取 {len(result)} 条数据")

def explain_code_logic():
    """解释代码逻辑"""
    print("\n" + "=" * 50)
    print("💡 代码逻辑解释")
    print("=" * 50)
    
    code_explanation = """
你问的这段代码的参数传递过程：

```python
args = GetStockDataParams(**arguments)
result = await get_stock_data(
    code=args.code,
    frequency=args.frequency,
    count=args.count,
    end_date=args.end_date
)
```

🔍 详细步骤：

1. **参数验证阶段**
   - `arguments` 是一个字典，包含外部传入的参数
   - `GetStockDataParams(**arguments)` 使用Pydantic进行参数验证
   - 如果参数类型错误或缺少必填参数，会抛出异常
   - 验证通过后创建 `args` 对象

2. **参数提取阶段**
   - `args.code` - 从验证后的对象中提取股票代码
   - `args.frequency` - 提取数据频率（有默认值）
   - `args.count` - 提取数据条数（有默认值）
   - `args.end_date` - 提取结束日期（可选参数）

3. **函数调用阶段**
   - 将提取的参数作为具名参数传递给 `get_stock_data` 函数
   - 函数执行并返回结果

🎯 这种方式的优点：
   ✓ 类型安全 - Pydantic确保参数类型正确
   ✓ 参数验证 - 自动验证必填参数和格式
   ✓ 默认值处理 - 自动填充默认值
   ✓ 代码清晰 - 参数传递过程一目了然
"""
    
    print(code_explanation)

async def main():
    """主函数"""
    # 基本演示
    await demo_parameter_passing()
    
    # 不同参数组合
    await demo_with_different_params()
    
    # 代码逻辑解释
    explain_code_logic()
    
    print("\n🎉 Demo完成！")

if __name__ == "__main__":
    asyncio.run(main())
