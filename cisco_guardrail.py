import os
import requests
from fastapi import HTTPException
from litellm.integrations.custom_guardrail import CustomGuardrail

class CiscoAIDefense(CustomGuardrail):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Lee las variables inyectadas automáticamente por el contenedor/.env
        self.api_key = os.getenv("AI_DEFENSE_API_KEY", "")
        self.endpoint = os.getenv(
            "AI_DEFENSE_ENDPOINT", 
            "https://eu.api.inspect.aidefense.security.cisco.com/api/v1/inspect/chat"
        )

    def _inspect_ai_defense(self, messages):
        """Llamada a la API de Cisco AI Defense"""
        if not self.api_key:
            print("[Cisco AI Defense] Advertencia: AI_DEFENSE_API_KEY no encontrada.")
            return None

        headers = {
            "Content-Type": "application/json",
            "X-Cisco-AI-Defense-API-Key": self.api_key
        }
        try:
            resp = requests.post(self.endpoint, json={"messages": messages}, headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[Cisco AI Defense] Error de conexión: {e}")
        return None

    # [ETAPA 1] Pre-Call Hook: Inspección de entrada del usuario
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        messages = data.get("messages", [])
        if not messages:
            return

        result = self._inspect_ai_defense(messages)
        if result and (result.get("action") == "Block" or not result.get("is_safe", True)):
            violations = [r.get("rule_name") for r in result.get("rules", [])]
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Input Security Violation Detected",
                    "guardrail": "Cisco AI Defense",
                    "stage": "pre_call",
                    "action": "Blocked",
                    "violations": violations,
                    "event_id": result.get("event_id")
                }
            )

    # [ETAPA 2] Post-Call Hook: Inspección de salida del modelo (Prevención de fuga de datos)
    async def async_post_call_success_hook(self, data, user_api_key_dict, response):
        if not response:
            return

        content = ""
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                content = choice.message.content
        elif isinstance(response, dict) and "choices" in response:
            content = response["choices"][0].get("message", {}).get("content", "")

        if not content:
            return

        out_messages = [{"role": "assistant", "content": content}]
        result = self._inspect_ai_defense(out_messages)

        if result and (result.get("action") == "Block" or not result.get("is_safe", True)):
            violations = [r.get("rule_name") for r in result.get("rules", [])]
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Output Security Violation Detected (Sensitive Data Leak)",
                    "guardrail": "Cisco AI Defense",
                    "stage": "post_call",
                    "action": "Blocked",
                    "violations": violations,
                    "event_id": result.get("event_id")
                }
            )

# Instancia exportada para LiteLLM
cisco_ai_defense = CiscoAIDefense()