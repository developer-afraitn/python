from sqlalchemy import select, desc
from app.storage.db import get_session
from app.storage.models.apiLogModel import ApiLog


class ApiLogRepo:

    def create(
        self,
        *,
        method: str,
        url: str,
        params: dict | None = None,
        request_body: dict | None = None,
        headers: dict | None = None,
        status_code: int | None = None,
        response: dict | None = None,
        duration_ms: int | None = None,
    ) -> ApiLog:
        with get_session() as db:
            row = ApiLog(
                method=method,
                url=url,
                params=params,
                request_body=request_body,
                headers=headers,
                status_code=status_code,
                response=response,
                duration_ms=duration_ms,
            )
            db.add(row)
            db.flush()
            db.refresh(row)
            return row

    def list(
        self,
        page: int = 1,
        limit: int = 20
    ) -> list[dict]:
        offset = (page - 1) * limit

        with get_session() as db:
            stmt = (
                select(ApiLog)
                .order_by(desc(ApiLog.id))
                .limit(limit)
                .offset(offset)
            )
            objs = db.execute(stmt).scalars().all()
            objs = list(reversed(objs))

            return [
                {
                    col.name: getattr(o, col.name)
                    for col in ApiLog.__table__.columns
                }
                for o in objs
            ]

