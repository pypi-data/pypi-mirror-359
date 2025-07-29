from abs_integration_core.repository import SubscriptionsRepository
from abs_repository_core.services.base_service import BaseService
from abs_integration_core.schema import Subscription
from typing import List


class SubscriptionService(BaseService):
    def __init__(self, subscription_repository: SubscriptionsRepository):
        super().__init__(subscription_repository)

    async def create(self, schema: Subscription) -> Subscription:
        subscription = super().add(schema)
        return Subscription(
            uuid=subscription.uuid,
            resource_type=subscription.resource_type,
            site_id=subscription.site_id,
            resource_id=subscription.resource_id,
            change_type=subscription.change_type,
            provider_name=subscription.provider_name,
            user_id=subscription.user_id
        )

    def remove_by_uuid(self, uuid: str) -> Subscription:
        id = self.get_by_attr("uuid", uuid).id
        return super().remove_by_id(id)

    async def list_subscriptions(self, provider_name: str, user_id: int) -> List[Subscription]:
        return await self._repository.list_subscriptions(provider_name, user_id)
