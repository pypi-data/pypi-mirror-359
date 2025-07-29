# src/autoagentsai/client.py
import json
import requests
from typing import Generator, Optional, List, Dict
from .types import ChatRequest, ImageInput




class AutoAgentsClient:
    def __init__(self, agent_id: str, auth_key: str, auth_secret: str, platform: str = "uat"):
        AUTOAGENTS_HOST = {
            "uat": "https://uat.agentspro.cn",
            "test": "https://test.agentspro.cn",
            "lingda": "https://lingda.agentspro.cn"
        }

        if platform not in AUTOAGENTS_HOST:
            raise ValueError(f"Unsupported platform: {platform}")
        self.agent_id = agent_id
        self.auth_key = auth_key
        self.auth_secret = auth_secret
        self.base_url = AUTOAGENTS_HOST[platform]
        self.headers = {
            "Authorization": f"Bearer {auth_key}.{auth_secret}",
            "Content-Type": "application/json"
        }

    def invoke(
        self,
        prompt: str,
        chat_id: Optional[str] = None,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False
    ) -> str:
        """非流式调用"""
        req = ChatRequest(
            agentId=self.agent_id,
            chatId=chat_id,
            userChatInput=prompt,
            images=[ImageInput(url=u) for u in images] if images else [],
            files=files or [],
            state=state or {},
            buttonKey=button_key or "",
            debug=debug
        )
        url = f"{self.base_url}/openapi/agents/chat/completions/v1"

        try:
            response = requests.post(url, headers=self.headers, json=req.model_dump(), timeout=30)
            if response.status_code == 200:
                return response.json()["choices"][0]["content"]
            return f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Exception: {str(e)}"

    def invoke_stream(
        self,
        prompt: str,
        chat_id: Optional[str] = None,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        state: Optional[Dict[str, str]] = None,
        button_key: Optional[str] = None,
        debug: bool = False
    ) -> Generator[str, None, None]:
        """流式调用，返回内容片段生成器"""
        req = ChatRequest(
            agentId=self.agent_id,
            chatId=chat_id,
            userChatInput=prompt,
            images=[ImageInput(url=u) for u in images] if images else [],
            files=files or [],
            state=state or {},
            buttonKey=button_key or "",
            debug=debug
        )
        url = f"{self.base_url}/openapi/agents/chat/stream/v1"

        try:
            response = requests.post(url, headers=self.headers, json=req.model_dump(), stream=True, timeout=30)
            if response.status_code != 200:
                yield f"Error {response.status_code}: {response.text}"
                return

            buffer = ""
            for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                if not chunk:
                    continue
                buffer += chunk

                while "\n\ndata:" in buffer or buffer.startswith("data:"):
                    if buffer.startswith("data:"):
                        end_pos = buffer.find("\n\n")
                        if end_pos == -1:
                            break
                        message = buffer[5:end_pos]
                        buffer = buffer[end_pos + 2:]
                    else:
                        start = buffer.find("\n\ndata:") + 7
                        end = buffer.find("\n\n", start)
                        if end == -1:
                            break
                        message = buffer[start:end]
                        buffer = buffer[end + 2:]

                    try:
                        data = json.loads(message)
                        if "content" in data and data["content"]:
                            try:
                                yield data["content"].encode("latin1").decode("utf-8")
                            except Exception:
                                yield data["content"]
                        if data.get("complete") or data.get("finish"):
                            return
                    except Exception:
                        continue
        except Exception as e:
            yield f"Stream error: {str(e)}"
