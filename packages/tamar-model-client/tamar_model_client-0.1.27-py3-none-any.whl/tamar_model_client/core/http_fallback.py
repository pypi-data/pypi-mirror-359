"""
HTTP fallback functionality for resilient clients

This module provides mixin classes for HTTP-based fallback when gRPC
connections fail, supporting both synchronous and asynchronous clients.
"""

import json
import logging
from typing import Optional, Iterator, AsyncIterator, Dict, Any

from . import generate_request_id, get_protected_logger
from ..schemas import ModelRequest, ModelResponse

logger = get_protected_logger(__name__)


class HttpFallbackMixin:
    """HTTP fallback functionality for synchronous clients"""
    
    def _ensure_http_client(self) -> None:
        """Ensure HTTP client is initialized"""
        if not hasattr(self, '_http_client') or not self._http_client:
            import requests
            self._http_client = requests.Session()
            
            # Set authentication header if available
            # Note: JWT token will be set per request in headers
            
            # Set default headers
            self._http_client.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'TamarModelClient/1.0'
            })
    
    def _convert_to_http_format(self, model_request: ModelRequest) -> Dict[str, Any]:
        """Convert ModelRequest to HTTP payload format"""
        payload = {
            "provider": model_request.provider.value,
            "model": model_request.model,
            "user_context": model_request.user_context.model_dump(),
            "stream": model_request.stream
        }
        
        # Add provider-specific fields
        if hasattr(model_request, 'messages') and model_request.messages:
            payload['messages'] = model_request.messages
        if hasattr(model_request, 'contents') and model_request.contents:
            payload['contents'] = model_request.contents
        
        # Add optional fields
        if model_request.channel:
            payload['channel'] = model_request.channel.value
        if model_request.invoke_type:
            payload['invoke_type'] = model_request.invoke_type.value
            
        # Add extra parameters
        if hasattr(model_request, 'model_extra') and model_request.model_extra:
            for key, value in model_request.model_extra.items():
                if key not in payload:
                    payload[key] = value
                
        return payload
    
    def _handle_http_stream(self, url: str, payload: Dict[str, Any], 
                           timeout: Optional[float], request_id: str, headers: Dict[str, str]) -> Iterator[ModelResponse]:
        """Handle HTTP streaming response"""
        import requests
        
        response = self._http_client.post(
            url,
            json=payload,
            timeout=timeout or 30,
            headers=headers,
            stream=True
        )
        response.raise_for_status()
        
        # Parse SSE stream
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        data = json.loads(data_str)
                        yield ModelResponse(**data)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse streaming response: {data_str}")
    
    def _invoke_http_fallback(self, model_request: ModelRequest, 
                             timeout: Optional[float] = None,
                             request_id: Optional[str] = None) -> Any:
        """HTTP fallback implementation"""
        self._ensure_http_client()
        
        # Generate request ID if not provided
        if not request_id:
            request_id = generate_request_id()
        
        # Log fallback usage
        logger.warning(
            f"🔻 Using HTTP fallback for request",
            extra={
                "request_id": request_id,
                "provider": model_request.provider.value,
                "model": model_request.model,
                "fallback_url": self.http_fallback_url
            }
        )
        
        # Convert to HTTP format
        http_payload = self._convert_to_http_format(model_request)
        
        # Construct URL
        url = f"{self.http_fallback_url}/v1/invoke"
        
        # Build headers with authentication
        headers = {'X-Request-ID': request_id}
        if hasattr(self, 'jwt_token') and self.jwt_token:
            headers['Authorization'] = f'Bearer {self.jwt_token}'
        
        if model_request.stream:
            # Return streaming iterator
            return self._handle_http_stream(url, http_payload, timeout, request_id, headers)
        else:
            # Non-streaming request
            response = self._http_client.post(
                url,
                json=http_payload,
                timeout=timeout or 30,
                headers=headers
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            return ModelResponse(**data)


class AsyncHttpFallbackMixin:
    """HTTP fallback functionality for asynchronous clients"""
    
    async def _ensure_http_client(self) -> None:
        """Ensure async HTTP client is initialized"""
        if not hasattr(self, '_http_session') or not self._http_session:
            import aiohttp
            self._http_session = aiohttp.ClientSession(
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'AsyncTamarModelClient/1.0'
                }
            )
            
            # Note: JWT token will be set per request in headers
    
    def _convert_to_http_format(self, model_request: ModelRequest) -> Dict[str, Any]:
        """Convert ModelRequest to HTTP payload format (reuse sync version)"""
        # This method doesn't need to be async, so we can reuse the sync version
        return HttpFallbackMixin._convert_to_http_format(self, model_request)
    
    async def _handle_http_stream(self, url: str, payload: Dict[str, Any],
                                 timeout: Optional[float], request_id: str, headers: Dict[str, str]) -> AsyncIterator[ModelResponse]:
        """Handle async HTTP streaming response"""
        import aiohttp
        
        timeout_obj = aiohttp.ClientTimeout(total=timeout or 30) if timeout else None
        
        async with self._http_session.post(
            url,
            json=payload,
            timeout=timeout_obj,
            headers=headers
        ) as response:
            response.raise_for_status()
            
            # Parse SSE stream
            async for line_bytes in response.content:
                if line_bytes:
                    line_str = line_bytes.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            yield ModelResponse(**data)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming response: {data_str}")
    
    async def _invoke_http_fallback(self, model_request: ModelRequest,
                                   timeout: Optional[float] = None,
                                   request_id: Optional[str] = None) -> Any:
        """Async HTTP fallback implementation"""
        await self._ensure_http_client()
        
        # Generate request ID if not provided
        if not request_id:
            request_id = generate_request_id()
        
        # Log fallback usage
        logger.warning(
            f"🔻 Using HTTP fallback for request",
            extra={
                "request_id": request_id,
                "provider": model_request.provider.value,
                "model": model_request.model,
                "fallback_url": self.http_fallback_url
            }
        )
        
        # Convert to HTTP format
        http_payload = self._convert_to_http_format(model_request)
        
        # Construct URL
        url = f"{self.http_fallback_url}/v1/invoke"
        
        # Build headers with authentication
        headers = {'X-Request-ID': request_id}
        if hasattr(self, 'jwt_token') and self.jwt_token:
            headers['Authorization'] = f'Bearer {self.jwt_token}'
        
        if model_request.stream:
            # Return async streaming iterator
            return self._handle_http_stream(url, http_payload, timeout, request_id, headers)
        else:
            # Non-streaming request
            import aiohttp
            timeout_obj = aiohttp.ClientTimeout(total=timeout or 30) if timeout else None
            
            async with self._http_session.post(
                url,
                json=http_payload,
                timeout=timeout_obj,
                headers=headers
            ) as response:
                response.raise_for_status()
                
                # Parse response
                data = await response.json()
                return ModelResponse(**data)
    
    async def _cleanup_http_session(self) -> None:
        """Clean up HTTP session"""
        if hasattr(self, '_http_session') and self._http_session:
            await self._http_session.close()
            self._http_session = None