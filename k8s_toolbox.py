#!/usr/bin/env python3
import os
import sys
import subprocess
from typing import List, Dict, Any


class K8sToolbox:
    def __init__(self):
        self.namespace = "default"
        self.context = ""

    def run_command(self, command: str, capture_output: bool = False) -> bool:
        """执行shell命令"""
        try:
            print(f"\n🚀 执行命令: {command}")
            if capture_output:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True)
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(f"错误输出: {result.stderr}")
                return result.returncode == 0
            else:
                result = subprocess.run(
                    command, shell=True, capture_output=False)
                return result.returncode == 0
        except Exception as e:
            print(f"❌ 命令执行失败: {e}")
            return False

    def check_kubectl_connection(self) -> bool:
        """检查kubectl连接状态"""
        try:
            result = subprocess.run(
                "kubectl cluster-info",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("❌ kubectl连接超时")
            return False
        except Exception as e:
            print(f"❌ kubectl连接检查失败: {e}")
            return False

    def show_menu(self) -> None:
        """显示主菜单"""
        print("\n" + "="*50)
        print("🛠️  Kubernetes 工具箱")
        print("="*50)
        print(f"📍 上下文: {self.context if self.context else 'N/A'}")
        print(f"🏷️  命名空间: {self.namespace}")
        print("-"*50)
        print("1. Pod 管理")
        print("2. Service 管理")
        print("3. Deployment 管理")
        print("4. ConfigMap/Secret 管理")
        print("5. 日志查看")
        print("6. 集群信息")
        print("7. 命名空间管理")
        print("8. 资源监控")
        print("9. 自定义命令")
        print("0. 退出")
        print("-"*50)

    def select_namespace_interactive(self) -> str:
        """交互式选择命名空间"""
        print(f"\n🔍 正在获取所有命名空间...")

        try:
            result = subprocess.run(
                "kubectl get namespaces --no-headers",
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )

            namespaces = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 1:
                        namespaces.append(parts[0])

            if not namespaces:
                print("❌ 未找到任何命名空间")
                return None

            current_idx = namespaces.index(
                self.namespace) if self.namespace in namespaces else 0

            print(f"\n🏷️  命名空间列表 (当前: {self.namespace}):")
            print("-" * 50)
            for i, ns in enumerate(namespaces, 1):
                marker = " ← 当前" if i == current_idx + 1 else ""
                print(f"{i:<4} {ns:<30} {marker}")
            print("-" * 50)

            while True:
                try:
                    choice = input(
                        f"\n请选择命名空间 (1-{len(namespaces)}), 或输入 'q' 返回: ").strip()

                    if choice.lower() in ['q', 'quit', 'exit']:
                        return None

                    choice_num = int(choice)
                    if 1 <= choice_num <= len(namespaces):
                        selected_ns = namespaces[choice_num - 1]
                        if selected_ns != self.namespace:
                            self.namespace = selected_ns
                            print(f"✅ 已切换到命名空间: {selected_ns}")
                        return selected_ns
                    else:
                        print(f"❌ 请输入 1 到 {len(namespaces)} 之间的数字")

                except ValueError:
                    print("❌ 请输入有效的数字")
                except KeyboardInterrupt:
                    print("\n👋 用户取消操作")
                    return None

        except subprocess.CalledProcessError as e:
            print(f"❌ 获取命名空间列表失败: {e}")
            if e.stderr:
                print(f"错误详情: {e.stderr}")
            return None
        except Exception as e:
            print(f"❌ 发生未知错误: {e}")
            return None

    def select_pod_interactive(self, namespace: str = None) -> str:
        """交互式选择Pod"""
        if not namespace:
            namespace = self.namespace

        print(f"\n🔍 正在获取命名空间 '{namespace}' 中的Pod列表...")

        # 获取Pod列表
        try:
            result = subprocess.run(
                f"kubectl get pods -n {namespace} --no-headers",
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )

            pods = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 1:
                        pods.append({
                            'name': parts[0],
                            'ready': parts[1] if len(parts) > 1 else '',
                            'status': parts[2] if len(parts) > 2 else '',
                            'restarts': parts[3] if len(parts) > 3 else '',
                            'age': ' '.join(parts[4:]) if len(parts) > 4 else ''
                        })

            if not pods:
                print(f"❌ 在命名空间 '{namespace}' 中未找到任何Pod")
                return None

            print(f"\n📋 命名空间 '{namespace}' 中的Pod列表:")
            print("-" * 80)
            print(
                f"{'序号':<4} {'Pod名称':<30} {'状态':<10} {'就绪':<10} {'重启次数':<10} {'运行时长':<15}")
            print("-" * 80)

            for i, pod in enumerate(pods, 1):
                print(
                    f"{i:<4} {pod['name']:<30} {pod['status']:<10} {pod['ready']:<10} {pod['restarts']:<10} {pod['age']:<15}")

            print("-" * 80)

            while True:
                try:
                    choice = input(
                        f"\n请选择Pod (1-{len(pods)}), 或输入 'q' 返回: ").strip()

                    if choice.lower() in ['q', 'quit', 'exit']:
                        return None

                    choice_num = int(choice)
                    if 1 <= choice_num <= len(pods):
                        selected_pod = pods[choice_num - 1]
                        print(
                            f"✅ 已选择Pod: {selected_pod['name']} (状态: {selected_pod['status']})")
                        return selected_pod['name']
                    else:
                        print(f"❌ 请输入 1 到 {len(pods)} 之间的数字")

                except ValueError:
                    print("❌ 请输入有效的数字")
                except KeyboardInterrupt:
                    print("\n👋 用户取消操作")
                    return None

        except subprocess.CalledProcessError as e:
            print(f"❌ 获取Pod列表失败: {e}")
            if e.stderr:
                print(f"错误详情: {e.stderr}")
            return None
        except Exception as e:
            print(f"❌ 发生未知错误: {e}")
            return None

    def pod_menu(self) -> None:
        """Pod管理子菜单"""
        while True:
            print("\n📦 Pod 管理")
            print("-" * 30)
            print("1. 查看所有Pod")
            print("2. 查看指定命名空间的Pod")
            print("3. 查看Pod详细信息")
            print("4. 删除Pod")
            print("5. 进入Pod容器")
            print("6. 查看Pod日志")
            print("7. 查看Pod资源使用")
            print("0. 返回上级菜单")

            choice = input("\n请选择操作 (0-7): ").strip()

            if choice == '1':
                cmd = f"kubectl get pods -A"
                self.run_command(cmd)

            elif choice == '2':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl get pods -n {ns}"
                self.run_command(cmd)

            elif choice == '3':
                pod_name = input("请输入Pod名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl describe pod {pod_name} -n {ns}"
                self.run_command(cmd)

            elif choice == '4':
                pod_name = input("请输入要删除的Pod名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                confirm = input(f"确认删除Pod {pod_name}? (y/N): ").strip().lower()
                if confirm == 'y':
                    cmd = f"kubectl delete pod {pod_name} -n {ns}"
                    self.run_command(cmd)

            elif choice == '5':
                pod_name = input("请输入Pod名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                container = input("请输入容器名称 (可选): ").strip()
                cmd = f"kubectl exec -it {pod_name} -n {ns}"
                if container:
                    cmd += f" -c {container}"
                cmd += " -- /bin/bash"
                self.run_command(cmd)

            elif choice == '6':
                pod_name = input("请输入Pod名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                lines = input("请输入显示行数 (默认: 100): ").strip() or "100"
                cmd = f"kubectl logs {pod_name} -n {ns} --tail={lines}"
                self.run_command(cmd)

            elif choice == '7':
                pod_name = input("请输入Pod名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl top pod {pod_name} -n {ns}"
                self.run_command(cmd)

            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")

    def service_menu(self) -> None:
        """Service管理子菜单"""
        while True:
            print("\n🌐 Service 管理")
            print("-" * 30)
            print("1. 查看所有Service")
            print("2. 查看指定命名空间的Service")
            print("3. 创建Service")
            print("4. 删除Service")
            print("5. 查看Service详情")
            print("0. 返回上级菜单")

            choice = input("\n请选择操作 (0-5): ").strip()

            if choice == '1':
                cmd = "kubectl get svc -A"
                self.run_command(cmd)

            elif choice == '2':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl get svc -n {ns}"
                self.run_command(cmd)

            elif choice == '3':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                name = input("请输入Service名称: ").strip()
                port = input("请输入端口号: ").strip()
                target_port = input("请输入目标端口: ").strip()
                cmd = f"""kubectl expose deployment {name} --port={port} --target-port={target_port} -n {ns}"""
                self.run_command(cmd)

            elif choice == '4':
                name = input("请输入要删除的Service名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                confirm = input(f"确认删除Service {name}? (y/N): ").strip().lower()
                if confirm == 'y':
                    cmd = f"kubectl delete svc {name} -n {ns}"
                    self.run_command(cmd)

            elif choice == '5':
                name = input("请输入Service名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl describe svc {name} -n {ns}"
                self.run_command(cmd)

            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")

    def deployment_menu(self) -> None:
        """Deployment管理子菜单"""
        while True:
            print("\n🚀 Deployment 管理")
            print("-" * 30)
            print("1. 查看所有Deployment")
            print("2. 查看指定命名空间的Deployment")
            print("3. 扩容/缩容Deployment")
            print("4. 重启Deployment")
            print("5. 删除Deployment")
            print("6. 查看Deployment详情")
            print("0. 返回上级菜单")

            choice = input("\n请选择操作 (0-6): ").strip()

            if choice == '1':
                cmd = "kubectl get deployments -A"
                self.run_command(cmd)

            elif choice == '2':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl get deployments -n {ns}"
                self.run_command(cmd)

            elif choice == '3':
                name = input("请输入Deployment名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                replicas = input("请输入副本数: ").strip()
                cmd = f"kubectl scale deployment {name} --replicas={replicas} -n {ns}"
                self.run_command(cmd)

            elif choice == '4':
                name = input("请输入Deployment名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl rollout restart deployment {name} -n {ns}"
                self.run_command(cmd)

            elif choice == '5':
                name = input("请输入要删除的Deployment名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                confirm = input(
                    f"确认删除Deployment {name}? (y/N): ").strip().lower()
                if confirm == 'y':
                    cmd = f"kubectl delete deployment {name} -n {ns}"
                    self.run_command(cmd)

            elif choice == '6':
                name = input("请输入Deployment名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl describe deployment {name} -n {ns}"
                self.run_command(cmd)

            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")

    def config_menu(self) -> None:
        """配置管理子菜单"""
        while True:
            print("\n⚙️  配置管理")
            print("-" * 30)
            print("1. 查看所有ConfigMap")
            print("2. 查看所有Secret")
            print("3. 创建ConfigMap")
            print("4. 创建Secret")
            print("5. 编辑ConfigMap")
            print("6. 编辑Secret")
            print("0. 返回上级菜单")

            choice = input("\n请选择操作 (0-6): ").strip()

            if choice == '1':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl get configmaps -n {ns}"
                self.run_command(cmd)

            elif choice == '2':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl get secrets -n {ns}"
                self.run_command(cmd)

            elif choice == '3':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                name = input("请输入ConfigMap名称: ").strip()
                cmd = f"kubectl create configmap {name} -n {ns} --from-file=."
                self.run_command(cmd)

            elif choice == '4':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                name = input("请输入Secret名称: ").strip()
                cmd = f"kubectl create secret generic {name} -n {ns} --from-literal=key=value"
                self.run_command(cmd)

            elif choice == '5':
                name = input("请输入ConfigMap名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl edit configmap {name} -n {ns}"
                self.run_command(cmd)

            elif choice == '6':
                name = input("请输入Secret名称: ").strip()
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl edit secret {name} -n {ns}"
                self.run_command(cmd)

            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")

    def log_menu(self) -> None:
        """日志查看子菜单"""
        while True:
            print("\n📋 日志查看")
            print("-" * 40)
            print("1. 查看Pod日志 (交互式选择)")
            print("2. 实时查看Pod日志 (交互式选择)")
            print("3. 查看多个Pod日志 (按标签)")
            print("4. 查看上一次容器日志 (交互式选择)")
            print("5. 切换命名空间")
            print("0. 返回上级菜单")
            print("-" * 40)

            choice = input("\n请选择操作 (0-5): ").strip()

            if choice == '1':
                # 查看Pod日志 - 交互式选择
                ns = self.select_namespace_interactive()
                if ns is None:
                    continue

                pod_name = self.select_pod_interactive(ns)
                if pod_name is None:
                    continue

                lines = input("请输入显示行数 (默认: 100): ").strip() or "100"
                cmd = f"kubectl logs {pod_name} -n {ns} --tail={lines}"
                self.run_command(cmd)

            elif choice == '2':
                # 实时查看Pod日志 - 交互式选择
                ns = self.select_namespace_interactive()
                if ns is None:
                    continue

                pod_name = self.select_pod_interactive(ns)
                if pod_name is None:
                    continue

                print(f"\n📡 开始实时查看Pod '{pod_name}' 的日志...")
                print("💡 按 Ctrl+C 停止实时日志")
                print("-" * 60)

                cmd = f"kubectl logs -f {pod_name} -n {ns}"
                # 对于实时日志，我们不捕获输出，直接执行
                try:
                    subprocess.run(cmd, shell=True)
                except KeyboardInterrupt:
                    print(f"\n⏹️  已停止实时日志查看")
                except Exception as e:
                    print(f"❌ 实时日志查看失败: {e}")

            elif choice == '3':
                # 查看多个Pod日志
                selector = input("请输入标签选择器 (如: app=nginx): ").strip()
                if not selector:
                    print("❌ 标签选择器不能为空")
                    continue

                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                lines = input("请输入显示行数 (默认: 50): ").strip() or "50"
                cmd = f"kubectl logs -l {selector} -n {ns} --tail={lines}"
                self.run_command(cmd)

            elif choice == '4':
                # 查看上一次容器日志 - 交互式选择
                ns = self.select_namespace_interactive()
                if ns is None:
                    continue

                pod_name = self.select_pod_interactive(ns)
                if pod_name is None:
                    continue

                cmd = f"kubectl logs {pod_name} -n {ns} --previous"
                self.run_command(cmd)

            elif choice == '5':
                # 切换命名空间
                ns = self.select_namespace_interactive()
                if ns:
                    print(f"✅ 当前命名空间已设置为: {ns}")

            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")

            # 除了实时日志外，其他操作完成后暂停
            if choice != '2':
                input("\n按回车键继续...")

    def cluster_menu(self) -> None:
        """集群信息子菜单"""
        while True:
            print("\n🌍 集群信息")
            print("-" * 30)
            print("1. 查看集群节点")
            print("2. 查看集群信息")
            print("3. 查看API资源")
            print("4. 查看存储类")
            print("5. 查看持久卷")
            print("0. 返回上级菜单")

            choice = input("\n请选择操作 (0-5): ").strip()

            if choice == '1':
                cmd = "kubectl get nodes -o wide"
                self.run_command(cmd)

            elif choice == '2':
                cmd = "kubectl cluster-info"
                self.run_command(cmd)

            elif choice == '3':
                cmd = "kubectl api-resources"
                self.run_command(cmd)

            elif choice == '4':
                cmd = "kubectl get storageclass"
                self.run_command(cmd)

            elif choice == '5':
                cmd = "kubectl get pv"
                self.run_command(cmd)

            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")

    def namespace_menu(self) -> None:
        """命名空间管理子菜单"""
        while True:
            print("\n🏷️  命名空间管理")
            print("-" * 30)
            print("1. 查看所有命名空间")
            print("2. 创建命名空间")
            print("3. 切换当前命名空间")
            print("4. 删除命名空间")
            print("0. 返回上级菜单")

            choice = input("\n请选择操作 (0-4): ").strip()

            if choice == '1':
                cmd = "kubectl get namespaces"
                self.run_command(cmd)

            elif choice == '2':
                name = input("请输入命名空间名称: ").strip()
                cmd = f"kubectl create namespace {name}"
                self.run_command(cmd)

            elif choice == '3':
                name = input("请输入要切换的命名空间名称: ").strip()
                self.namespace = name
                print(f"✅ 当前命名空间已切换到: {name}")

            elif choice == '4':
                name = input("请输入要删除的命名空间名称: ").strip()
                confirm = input(f"确认删除命名空间 {name}? (y/N): ").strip().lower()
                if confirm == 'y':
                    cmd = f"kubectl delete namespace {name}"
                    self.run_command(cmd)

            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")

    def monitor_menu(self) -> None:
        """资源监控子菜单"""
        while True:
            print("\n📊 资源监控")
            print("-" * 30)
            print("1. 查看节点资源使用")
            print("2. 查看Pod资源使用")
            print("3. 查看Top节点")
            print("4. 查看事件")
            print("0. 返回上级菜单")

            choice = input("\n请选择操作 (0-4): ").strip()

            if choice == '1':
                cmd = "kubectl top nodes"
                self.run_command(cmd)

            elif choice == '2':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl top pods -n {ns}"
                self.run_command(cmd)

            elif choice == '3':
                cmd = "kubectl top nodes"
                self.run_command(cmd)

            elif choice == '4':
                ns = input(
                    f"请输入命名空间 (默认: {self.namespace}): ").strip() or self.namespace
                cmd = f"kubectl get events -n {ns} --sort-by='.lastTimestamp'"
                self.run_command(cmd)

            elif choice == '0':
                break
            else:
                print("❌ 无效选择，请重新输入")

    def custom_command(self) -> None:
        """自定义命令"""
        print("\n⌨️  自定义命令")
        print("-" * 30)
        print("输入您要执行的kubectl命令")
        print("例如: kubectl get pods -A")
        print("输入 'quit' 返回上级菜单")

        while True:
            command = input("\nkubectl> ").strip()

            if command.lower() in ['quit', 'exit', 'q']:
                break

            if command:
                # 检查是否是kubectl命令
                if not command.startswith('kubectl'):
                    add_kubectl = input(
                        "是否添加 'kubectl' 前缀? (Y/n): ").strip().lower()
                    if add_kubectl != 'n':
                        command = f"kubectl {command}"

                self.run_command(command)

    def run(self) -> None:
        """运行主程序"""
        print("🎉 欢迎使用 Kubernetes 工具箱!")

        # 检查kubectl是否可用
        if not self.run_command("kubectl version --client", capture_output=True):
            print("❌ 未找到kubectl，请确保kubectl已安装并配置正确")
            return

        # 检查集群连接
        if not self.check_kubectl_connection():
            print("❌ 无法连接到Kubernetes集群，请检查kubeconfig配置")
            response = input("是否继续? (y/N): ").strip().lower()
            if response != 'y':
                return

        # 获取当前上下文和命名空间
        try:
            context_result = subprocess.run(
                "kubectl config current-context",
                shell=True,
                capture_output=True,
                text=True
            )
            if context_result.returncode == 0:
                self.context = context_result.stdout.strip()
                print(f"📍 当前上下文: {self.context}")

            ns_result = subprocess.run(
                "kubectl config view --minify --output 'jsonpath={..namespace}'",
                shell=True,
                capture_output=True,
                text=True
            )
            if ns_result.returncode == 0 and ns_result.stdout.strip():
                self.namespace = ns_result.stdout.strip()
                print(f"🏷️  当前命名空间: {self.namespace}")
            else:
                print(f"🏷️  当前命名空间: {self.namespace} (默认)")

        except Exception as e:
            print(f"⚠️  获取上下文信息失败: {e}")

        while True:
            self.show_menu()
            choice = input("请选择功能模块 (0-9): ").strip()

            if choice == '1':
                self.pod_menu()
            elif choice == '2':
                self.service_menu()
            elif choice == '3':
                self.deployment_menu()
            elif choice == '4':
                self.config_menu()
            elif choice == '5':
                self.log_menu()
            elif choice == '6':
                self.cluster_menu()
            elif choice == '7':
                self.namespace_menu()
            elif choice == '8':
                self.monitor_menu()
            elif choice == '9':
                self.custom_command()
            elif choice == '0':
                print("👋 感谢使用 Kubernetes 工具箱!")
                break
            else:
                print("❌ 无效选择，请重新输入")


def main():
    toolbox = K8sToolbox()
    toolbox.run()


if __name__ == "__main__":
    main()
