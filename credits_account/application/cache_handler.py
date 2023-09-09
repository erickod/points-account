from typing import Union
from uuid import UUID


class CreditCacheHandler:
    @staticmethod
    def clean_credits_cache_by_company_id(company_id: Union[str, UUID]) -> None:
        return

        from automation.signals import delete_keys_from_redis
        from company.models import Company

        company_id = str(company_id)
        company_as_orm_model = Company.objects.get(id=company_id)
        company_id_as_redis_key = f"*{company_id}*"
        company_slug_as_redis_key = f"*{company_as_orm_model.slug}*"
        delete_keys_from_redis(company_id_as_redis_key)
        delete_keys_from_redis(company_slug_as_redis_key)
