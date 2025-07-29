from spryx_http import SpryxAsyncClient


class OrgConfig:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client

    async def create_org_config(
        self,
        organization_id: str,
        embedding_llm_models: list[str],
        completion_llm_models: list[str],
        audio_transcription_llm_models: list[str],
    ) -> dict:
        """List all vector stores."""
        payload = {
            "org_id": organization_id,
            "embedding_llm_models": embedding_llm_models,
            "completion_llm_models": completion_llm_models,
            "audio_transcription_llm_models": audio_transcription_llm_models,
        }
        return await self._client.post(
            "/v1/org-config",
            json=payload,
            headers={"x-organization-id": organization_id},
        )
        
        
        
        

   