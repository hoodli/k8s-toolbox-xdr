#!/bin/bash

echo "🚀 安装 Kubernetes 工具箱..."

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 请先安装Python3"
    exit 1
fi

# 检查pip3
if ! command -v pip3 &> /dev/null; then
    echo "❌ 请先安装pip3"
    exit 1
fi

# 检查kubectl
if ! command -v kubectl &> /dev/null; then
    echo "⚠️  未找到kubectl，请先安装kubectl"
fi

# 设置权限
chmod +x k8s_toolbox.py

# 创建别名
SCRIPT_DIR=$(pwd)
echo "" >> ~/.bashrc
echo "# Kubernetes Toolbox" >> ~/.bashrc
echo "alias ktool='python3 $SCRIPT_DIR/k8s_toolbox.py'" >> ~/.bashrc

echo "" >> ~/.zshrc
echo "# Kubernetes Toolbox" >> ~/.zshrc
echo "alias ktool='python3 $SCRIPT_DIR/k8s_toolbox.py'" >> ~/.zshrc

echo "✅ 安装完成!"
echo ""
echo "使用方法:"
echo "  python3 k8s_toolbox.py"
echo "  或者重启终端后使用: ktool"
echo ""
echo "🎯 新特性:"
echo "  - 交互式Pod选择"
echo "  - 自动列出当前命名空间Pod"
echo "  - 实时日志查看优化"
echo "  - 美观的表格显示"
echo ""
