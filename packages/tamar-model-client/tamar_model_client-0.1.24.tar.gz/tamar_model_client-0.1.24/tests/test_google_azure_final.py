#!/usr/bin/env python3
"""
简化版的 Google/Azure 场景测试脚本
只保留基本调用和打印功能
"""

import asyncio
import logging
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple

# 配置测试脚本专用的日志
# 使用特定的logger名称，避免影响客户端日志
test_logger = logging.getLogger('test_google_azure_final')
test_logger.setLevel(logging.INFO)
test_logger.propagate = False  # 不传播到根logger

# 创建测试脚本专用的handler
test_handler = logging.StreamHandler()
test_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
test_logger.addHandler(test_handler)

logger = test_logger

os.environ['MODEL_MANAGER_SERVER_GRPC_USE_TLS'] = "true"
os.environ['MODEL_MANAGER_SERVER_ADDRESS'] = "localhost:50051"
os.environ['MODEL_MANAGER_SERVER_JWT_SECRET_KEY'] = "model-manager-server-jwt-key"

# 导入客户端模块
try:
    from tamar_model_client import TamarModelClient, AsyncTamarModelClient
    from tamar_model_client.schemas import ModelRequest, UserContext
    from tamar_model_client.enums import ProviderType, InvokeType, Channel
    
    # 为了调试，临时启用 SDK 的日志输出
    # 注意：这会输出 JSON 格式的日志
    import os
    os.environ['TAMAR_MODEL_CLIENT_LOG_LEVEL'] = 'INFO'
    
except ImportError as e:
    logger.error(f"导入模块失败: {e}")
    sys.exit(1)


def test_google_ai_studio():
    """测试 Google AI Studio"""
    print("\n🔍 测试 Google AI Studio...")

    try:
        client = TamarModelClient()

        request = ModelRequest(
            provider=ProviderType.GOOGLE,
            channel=Channel.AI_STUDIO,
            invoke_type=InvokeType.GENERATION,
            model="tamar-google-gemini-flash-lite",
            contents=[
                {"role": "user", "parts": [{"text": "Hello, how are you?"}]}
            ],
            user_context=UserContext(
                user_id="test_user",
                org_id="test_org",
                client_type="test_client"
            ),
            config={
                "temperature": 0.7,
                "maxOutputTokens": 100
            }
        )

        response = client.invoke(request)
        print(f"✅ Google AI Studio 成功")
        print(f"   响应类型: {type(response)}")
        print(f"   响应内容: {str(response)[:200]}...")

    except Exception as e:
        print(f"❌ Google AI Studio 失败: {str(e)}")


def test_google_vertex_ai():
    """测试 Google Vertex AI"""
    print("\n🔍 测试 Google Vertex AI...")

    try:
        client = TamarModelClient()

        request = ModelRequest(
            provider=ProviderType.GOOGLE,
            channel=Channel.VERTEXAI,
            invoke_type=InvokeType.GENERATION,
            model="tamar-google-gemini-flash-lite",
            contents=[
                {"role": "user", "parts": [{"text": "What is AI?"}]}
            ],
            user_context=UserContext(
                user_id="test_user",
                org_id="test_org",
                client_type="test_client"
            ),
            config={
                "temperature": 0.5
            }
        )

        response = client.invoke(request)
        print(f"✅ Google Vertex AI 成功")
        print(f"   响应类型: {type(response)}")
        print(f"   响应内容: {str(response)[:200]}...")

    except Exception as e:
        print(f"❌ Google Vertex AI 失败: {str(e)}")


def test_azure_openai():
    """测试 Azure OpenAI"""
    print("\n☁️  测试 Azure OpenAI...")

    try:
        client = TamarModelClient()

        request = ModelRequest(
            provider=ProviderType.AZURE,
            invoke_type=InvokeType.CHAT_COMPLETIONS,
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Hello, how are you?"}
            ],
            user_context=UserContext(
                user_id="test_user",
                org_id="test_org",
                client_type="test_client"
            ),
        )

        response = client.invoke(request)
        print(f"✅ Azure OpenAI 成功")
        print(f"   响应内容: {response.model_dump_json()}...")

    except Exception as e:
        print(f"❌ Azure OpenAI 失败: {str(e)}")


async def test_google_streaming():
    """测试 Google 流式响应"""
    print("\n📡 测试 Google 流式响应...")

    try:
        async with AsyncTamarModelClient() as client:
            request = ModelRequest(
                provider=ProviderType.GOOGLE,
                channel=Channel.AI_STUDIO,
                invoke_type=InvokeType.GENERATION,
                model="tamar-google-gemini-flash-lite",
                contents=[
                    {"role": "user", "parts": [{"text": "Count 1 to 5"}]}
                ],
                user_context=UserContext(
                    user_id="test_user",
                    org_id="test_org",
                    client_type="test_client"
                ),
                stream=True,
                config={
                    "temperature": 0.1,
                    "maxOutputTokens": 50
                }
            )

            response_gen = await client.invoke(request)
            print(f"✅ Google 流式调用成功")
            print(f"   响应类型: {type(response_gen)}")

            chunk_count = 0
            async for chunk in response_gen:
                chunk_count += 1
                print(f"   数据块 {chunk_count}: {type(chunk)} - {chunk.model_dump_json()}...")
                if chunk_count >= 3:  # 只显示前3个数据块
                    break

    except Exception as e:
        print(f"❌ Google 流式响应失败: {str(e)}")


async def test_azure_streaming():
    """测试 Azure 流式响应"""
    print("\n📡 测试 Azure 流式响应...")

    try:
        async with AsyncTamarModelClient() as client:
            request = ModelRequest(
                provider=ProviderType.AZURE,
                channel=Channel.OPENAI,
                invoke_type=InvokeType.CHAT_COMPLETIONS,
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": "Count 1 to 5"}
                ],
                user_context=UserContext(
                    user_id="test_user",
                    org_id="test_org",
                    client_type="test_client"
                ),
                stream=True  # 添加流式参数
            )

            response_gen = await client.invoke(request)
            print(f"✅ Azure 流式调用成功")
            print(f"   响应类型: {type(response_gen)}")

            chunk_count = 0
            async for chunk in response_gen:
                chunk_count += 1
                print(f"   数据块 {chunk_count}: {type(chunk)} - {chunk.model_dump_json()}...")
                if chunk_count >= 3:  # 只显示前3个数据块
                    break

    except Exception as e:
        print(f"❌ Azure 流式响应失败: {str(e)}")


def test_sync_batch_requests():
    """测试同步批量请求"""
    print("\n📦 测试同步批量请求...")

    try:
        from tamar_model_client.schemas import BatchModelRequest, BatchModelRequestItem

        with TamarModelClient() as client:
            # 构建批量请求，包含 Google 和 Azure 的多个请求
            batch_request = BatchModelRequest(
                user_context=UserContext(
                    user_id="test_user",
                    org_id="test_org",
                    client_type="test_client"
                ),
                items=[
                    # Google AI Studio 请求
                    BatchModelRequestItem(
                        provider=ProviderType.GOOGLE,
                        invoke_type=InvokeType.GENERATION,
                        model="tamar-google-gemini-flash-lite",
                        contents=[
                            {"role": "user", "parts": [{"text": "Hello from sync batch - Google AI Studio"}]}
                        ],
                        custom_id="sync-google-ai-studio-1",
                    ),
                    # Azure OpenAI 请求
                    BatchModelRequestItem(
                        provider=ProviderType.AZURE,
                        invoke_type=InvokeType.CHAT_COMPLETIONS,
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "user", "content": "Hello from sync batch - Azure OpenAI"}
                        ],
                        custom_id="sync-azure-openai-1",
                    ),
                    # 再添加一个 Azure 请求
                    BatchModelRequestItem(
                        provider=ProviderType.AZURE,
                        invoke_type=InvokeType.CHAT_COMPLETIONS,
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "user", "content": "What is 2+2?"}
                        ],
                        custom_id="sync-azure-openai-2",
                    )
                ]
            )

            # 执行批量请求
            batch_response = client.invoke_batch(batch_request)

            print(f"✅ 同步批量请求成功")
            print(f"   请求数量: {len(batch_request.items)}")
            print(f"   响应数量: {len(batch_response.responses)}")
            print(f"   批量请求ID: {batch_response.request_id}")

            # 显示每个响应的结果
            for i, response in enumerate(batch_response.responses):
                print(f"\n   响应 {i + 1}:")
                print(f"   - custom_id: {response.custom_id}")
                print(f"   - 内容长度: {len(response.content) if response.content else 0}")
                print(f"   - 有错误: {'是' if response.error else '否'}")
                if response.content:
                    print(f"   - 内容预览: {response.content[:100]}...")
                if response.error:
                    print(f"   - 错误信息: {response.error}")

    except Exception as e:
        print(f"❌ 同步批量请求失败: {str(e)}")


async def test_batch_requests():
    """测试异步批量请求"""
    print("\n📦 测试异步批量请求...")

    try:
        from tamar_model_client.schemas import BatchModelRequest, BatchModelRequestItem

        async with AsyncTamarModelClient() as client:
            # 构建批量请求，包含 Google 和 Azure 的多个请求
            batch_request = BatchModelRequest(
                user_context=UserContext(
                    user_id="test_user",
                    org_id="test_org",
                    client_type="test_client"
                ),
                items=[
                    # Google AI Studio 请求
                    BatchModelRequestItem(
                        provider=ProviderType.GOOGLE,
                        invoke_type=InvokeType.GENERATION,
                        model="tamar-google-gemini-flash-lite",
                        contents=[
                            {"role": "user", "parts": [{"text": "Hello from Google AI Studio"}]}
                        ],
                        custom_id="google-ai-studio-1",
                    ),
                    # Google Vertex AI 请求
                    BatchModelRequestItem(
                        provider=ProviderType.GOOGLE,
                        channel=Channel.VERTEXAI,
                        invoke_type=InvokeType.GENERATION,
                        model="tamar-google-gemini-flash-lite",
                        contents=[
                            {"role": "user", "parts": [{"text": "Hello from Google Vertex AI"}]}
                        ],
                        custom_id="google-vertex-ai-1",
                    ),
                    # Azure OpenAI 请求
                    BatchModelRequestItem(
                        provider=ProviderType.AZURE,
                        invoke_type=InvokeType.CHAT_COMPLETIONS,
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "user", "content": "Hello from Azure OpenAI"}
                        ],
                        custom_id="azure-openai-1",
                    ),
                    # 再添加一个 Azure 请求
                    BatchModelRequestItem(
                        provider=ProviderType.AZURE,
                        invoke_type=InvokeType.CHAT_COMPLETIONS,
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "user", "content": "What is the capital of France?"}
                        ],
                        custom_id="azure-openai-2",
                    )
                ]
            )

            # 执行批量请求
            batch_response = await client.invoke_batch(batch_request)

            print(f"✅ 批量请求成功")
            print(f"   请求数量: {len(batch_request.items)}")
            print(f"   响应数量: {len(batch_response.responses)}")
            print(f"   批量请求ID: {batch_response.request_id}")

            # 显示每个响应的结果
            for i, response in enumerate(batch_response.responses):
                print(f"\n   响应 {i + 1}:")
                print(f"   - custom_id: {response.custom_id}")
                print(f"   - 内容长度: {len(response.content) if response.content else 0}")
                print(f"   - 有错误: {'是' if response.error else '否'}")
                if response.content:
                    print(f"   - 内容预览: {response.content[:100]}...")
                if response.error:
                    print(f"   - 错误信息: {response.error}")

    except Exception as e:
        print(f"❌ 批量请求失败: {str(e)}")


def test_concurrent_requests(num_requests: int = 150):
    """测试并发请求
    
    Args:
        num_requests: 要发送的总请求数，默认150个
    """
    print(f"\n🚀 测试并发请求 ({num_requests} 个请求)...")

    # 统计变量
    total_requests = 0
    successful_requests = 0
    failed_requests = 0
    request_times: List[float] = []
    errors: Dict[str, int] = {}

    # 线程安全的锁
    stats_lock = threading.Lock()

    def make_single_request(request_id: int) -> Tuple[bool, float, str]:
        """执行单个请求并返回结果
        
        Returns:
            (success, duration, error_msg)
        """
        start_time = time.time()
        try:
            # 每个线程创建自己的客户端实例
            client = TamarModelClient()

            # Google Vertex AI
            request = ModelRequest(
                provider=ProviderType.GOOGLE,
                channel=Channel.VERTEXAI,
                invoke_type=InvokeType.GENERATION,
                model="tamar-google-gemini-flash-lite",
                contents="1+1等于几？",
                user_context=UserContext(
                    user_id=f"{os.environ.get('INSTANCE_ID', '0')}_{request_id:03d}",
                    org_id="test_org",
                    client_type="concurrent_test"
                ),
                config={"temperature": 0.1}
            )

            response = client.invoke(request, timeout=300000.0)
            duration = time.time() - start_time
            return (True, duration, "")

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            return (False, duration, error_msg)

    def worker(request_id: int):
        """工作线程函数"""
        nonlocal total_requests, successful_requests, failed_requests

        success, duration, error_msg = make_single_request(request_id)

        with stats_lock:
            total_requests += 1
            request_times.append(duration)

            if success:
                successful_requests += 1
            else:
                failed_requests += 1
                # 统计错误类型
                error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg[:50]
                errors[error_type] = errors.get(error_type, 0) + 1

            # 每20个请求输出一次进度
            if total_requests % 20 == 0:
                print(
                    f"   进度: {total_requests}/{num_requests} (成功: {successful_requests}, 失败: {failed_requests})")

    # 使用线程池执行并发请求
    start_time = time.time()

    # 使用线程池，最多50个并发线程
    with ThreadPoolExecutor(max_workers=50) as executor:
        # 提交所有任务
        futures = [executor.submit(worker, i) for i in range(num_requests)]

        # 等待所有任务完成
        for future in futures:
            future.result()

    total_duration = time.time() - start_time

    # 计算统计信息
    avg_request_time = sum(request_times) / len(request_times) if request_times else 0
    min_request_time = min(request_times) if request_times else 0
    max_request_time = max(request_times) if request_times else 0

    # 输出结果
    print(f"\n📊 并发测试结果:")
    print(f"   总请求数: {total_requests}")
    print(f"   成功请求: {successful_requests} ({successful_requests / total_requests * 100:.1f}%)")
    print(f"   失败请求: {failed_requests} ({failed_requests / total_requests * 100:.1f}%)")
    print(f"   总耗时: {total_duration:.2f} 秒")
    print(f"   平均QPS: {total_requests / total_duration:.2f}")
    print(f"\n   请求耗时统计:")
    print(f"   - 平均: {avg_request_time:.3f} 秒")
    print(f"   - 最小: {min_request_time:.3f} 秒")
    print(f"   - 最大: {max_request_time:.3f} 秒")

    if errors:
        print(f"\n   错误统计:")
        for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {error_type}: {count} 次")

    return {
        "total": total_requests,
        "successful": successful_requests,
        "failed": failed_requests,
        "duration": total_duration,
        "qps": total_requests / total_duration
    }


async def test_async_concurrent_requests(num_requests: int = 150):
    """测试异步并发请求
    
    Args:
        num_requests: 要发送的总请求数，默认150个
    """
    print(f"\n🚀 测试异步并发请求 ({num_requests} 个请求)...")

    # 统计变量
    total_requests = 0
    successful_requests = 0
    failed_requests = 0
    request_times: List[float] = []
    errors: Dict[str, int] = {}

    # 异步锁
    stats_lock = asyncio.Lock()

    async def make_single_async_request(client: AsyncTamarModelClient, request_id: int) -> Tuple[bool, float, str]:
        """执行单个异步请求并返回结果
        
        Returns:
            (success, duration, error_msg)
        """
        start_time = time.time()
        try:
            # 根据请求ID选择不同的provider，以增加测试多样性
            # Google Vertex AI
            request = ModelRequest(
                provider=ProviderType.GOOGLE,
                channel=Channel.VERTEXAI,
                invoke_type=InvokeType.GENERATION,
                model="tamar-google-gemini-flash-lite",
                contents="1+1等于几？",
                user_context=UserContext(
                    user_id=f"{os.environ.get('INSTANCE_ID', '0')}_{request_id:03d}",
                    org_id="test_org",
                    client_type="async_concurrent_test"
                ),
                config={"temperature": 0.1}
            )

            response = await client.invoke(request, timeout=300000.0)
            duration = time.time() - start_time
            return (True, duration, "")

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            return (False, duration, error_msg)

    async def async_worker(client: AsyncTamarModelClient, request_id: int):
        """异步工作协程"""
        nonlocal total_requests, successful_requests, failed_requests

        success, duration, error_msg = await make_single_async_request(client, request_id)

        async with stats_lock:
            total_requests += 1
            request_times.append(duration)

            if success:
                successful_requests += 1
            else:
                failed_requests += 1
                # 统计错误类型
                error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg[:50]
                errors[error_type] = errors.get(error_type, 0) + 1

            # 每20个请求输出一次进度
            if total_requests % 20 == 0:
                print(
                    f"   进度: {total_requests}/{num_requests} (成功: {successful_requests}, 失败: {failed_requests})")

    # 使用异步客户端执行并发请求
    start_time = time.time()

    # 创建一个共享的异步客户端
    async with AsyncTamarModelClient() as client:
        # 创建所有任务，但限制并发数
        semaphore = asyncio.Semaphore(50)  # 限制最多50个并发请求

        async def limited_worker(request_id: int):
            async with semaphore:
                await async_worker(client, request_id)

        # 创建所有任务
        tasks = [limited_worker(i) for i in range(num_requests)]

        # 等待所有任务完成
        await asyncio.gather(*tasks)

    total_duration = time.time() - start_time

    # 计算统计信息
    avg_request_time = sum(request_times) / len(request_times) if request_times else 0
    min_request_time = min(request_times) if request_times else 0
    max_request_time = max(request_times) if request_times else 0

    # 输出结果
    print(f"\n📊 异步并发测试结果:")
    print(f"   总请求数: {total_requests}")
    print(f"   成功请求: {successful_requests} ({successful_requests / total_requests * 100:.1f}%)")
    print(f"   失败请求: {failed_requests} ({failed_requests / total_requests * 100:.1f}%)")
    print(f"   总耗时: {total_duration:.2f} 秒")
    print(f"   平均QPS: {total_requests / total_duration:.2f}")
    print(f"\n   请求耗时统计:")
    print(f"   - 平均: {avg_request_time:.3f} 秒")
    print(f"   - 最小: {min_request_time:.3f} 秒")
    print(f"   - 最大: {max_request_time:.3f} 秒")

    if errors:
        print(f"\n   错误统计:")
        for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {error_type}: {count} 次")

    return {
        "total": total_requests,
        "successful": successful_requests,
        "failed": failed_requests,
        "duration": total_duration,
        "qps": total_requests / total_duration
    }


async def main():
    """主函数"""
    print("🚀 简化版 Google/Azure 测试")
    print("=" * 50)

    try:
        # # 同步测试
        # test_google_ai_studio()
        # test_google_vertex_ai()
        # test_azure_openai()
        #
        # # 同步批量测试
        # test_sync_batch_requests()
        #
        # # 异步流式测试
        # await asyncio.wait_for(test_google_streaming(), timeout=60.0)
        # await asyncio.wait_for(test_azure_streaming(), timeout=60.0)
        #
        # # 异步批量测试
        # await asyncio.wait_for(test_batch_requests(), timeout=120.0)

        # 同步并发测试
        #test_concurrent_requests(150)  # 测试150个并发请求

        # 异步并发测试
        await test_async_concurrent_requests(50)  # 测试150个异步并发请求

        print("\n✅ 测试完成")

    except asyncio.TimeoutError:
        print("\n⏰ 测试超时")
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")
    finally:
        # 简单优雅的任务清理
        print("📝 清理异步任务...")
        try:
            # 短暂等待让正在完成的任务自然结束
            await asyncio.sleep(0.5)

            # 检查是否还有未完成的任务
            current_task = asyncio.current_task()
            tasks = [task for task in asyncio.all_tasks()
                     if not task.done() and task != current_task]

            if tasks:
                print(f"   发现 {len(tasks)} 个未完成任务，等待自然完成...")
                # 简单等待，不强制取消
                try:
                    await asyncio.wait_for(
                        asyncio.sleep(2.0),  # 给任务2秒时间自然完成
                        timeout=2.0
                    )
                except asyncio.TimeoutError:
                    pass

            print("   任务清理完成")

        except Exception as e:
            print(f"   ⚠️ 任务清理时出现异常: {e}")

        print("🔚 程序即将退出")


if __name__ == "__main__":
    try:
        # 临时降低 asyncio 日志级别，减少任务取消时的噪音
        asyncio_logger = logging.getLogger('asyncio')
        original_level = asyncio_logger.level
        asyncio_logger.setLevel(logging.ERROR)

        try:
            asyncio.run(main())
        finally:
            # 恢复原始日志级别
            asyncio_logger.setLevel(original_level)

    except KeyboardInterrupt:
        print("\n⚠️ 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
    finally:
        print("🏁 程序已退出")
